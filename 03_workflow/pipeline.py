import os
import urllib

from steps.preprocess import preprocess
from steps.train import train
from steps.test import test
from steps.register import register
from steps.deploy import deploy

from sagemaker.s3 import S3Uploader
from sagemaker.session import Session
from sagemaker import get_execution_role
from sagemaker.workflow.function_step import step
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.parameters import (
    ParameterBoolean,
    ParameterFloat, ParameterInteger
)

import mlflow
from sagemaker.workflow.execution_variables import ExecutionVariables
from sagemaker.workflow.pipeline_definition_config import PipelineDefinitionConfig
from sagemaker.workflow.pipeline_experiment_config import PipelineExperimentConfig
from sagemaker.workflow.pipeline_context import LocalPipelineSession

def download_data_and_upload_to_s3(bucket_name):
    file_name = "predictive_maintenance_raw_data_header.csv"
    s3_prefix = "sagemaker-btd"
    s3_uri = f"s3://{bucket_name}/{s3_prefix}"

    input_data_dir = "/tmp/data/"
    input_data_path = os.path.join(input_data_dir, 'predictive_maintenance_raw_data_header.csv')
    os.makedirs(os.path.dirname(input_data_path), exist_ok=True)
    
    dataset_url = "http://archive.ics.uci.edu/ml/machine-learning-databases/00601/ai4i2020.csv"
    urllib.request.urlretrieve(dataset_url, input_data_path)

    upload_s3_uri = S3Uploader.upload(input_data_path, s3_uri)
    print("Downloading dataset and uploading to Amazon S3...")
    print(upload_s3_uri)

    return upload_s3_uri

def create_steps(role, input_data_s3_uri, project_prefix, bucket_name,
                 model_package_group_name, model_approval_status,
                 eta_parameter, max_depth_parameter, deploy_model_parameter, experiment_name, run_name, mlflow_arn):

    env_variables={'MLFLOW_TRACKING_ARN':mlflow_arn}
    
    preprocess_result = step(preprocess, name="Preprocess", job_name_prefix=f"{project_prefix}-Preprocess", 
                             keep_alive_period_in_seconds=300, environment_variables=env_variables)(
                            input_data_s3_uri, experiment_name, run_name)
    
    train_result = step(train, name="Train", job_name_prefix=f"{project_prefix}-Train",
                        keep_alive_period_in_seconds=300, environment_variables=env_variables)(
                        X_train=preprocess_result[0], y_train=preprocess_result[1], 
                        X_val=preprocess_result[2], y_val=preprocess_result[3],
                        eta=eta_parameter, max_depth=max_depth_parameter, experiment_name=experiment_name, run_id=preprocess_result[7])

    test_result = step(test, name="Evaluate", job_name_prefix=f"{project_prefix}-Test",
                       keep_alive_period_in_seconds=300, environment_variables=env_variables)(
                        featurizer_model=preprocess_result[6], booster=train_result, 
                        X_test=preprocess_result[4], y_test=preprocess_result[5], experiment_name=experiment_name, run_id=preprocess_result[7])

    register_result = step(register, name="Register", job_name_prefix=f"{project_prefix}-Register",
                           keep_alive_period_in_seconds=300, environment_variables=env_variables)(
                        role,featurizer_model=preprocess_result[6], booster=train_result, 
                        bucket_name=bucket_name, model_report_dict=test_result,
                        model_package_group_name=model_package_group_name,
                        model_approval_status=model_approval_status, experiment_name=experiment_name, run_id=preprocess_result[7])

    deploy_result = step(deploy, name="Deploy", job_name_prefix=f"{project_prefix}-Deploy",
                         keep_alive_period_in_seconds=300, environment_variables=env_variables)(
                    role, project_prefix,model_package_arn=register_result, 
                    deploy_model=deploy_model_parameter, experiment_name=experiment_name, run_id=preprocess_result[7])

    return [deploy_result]

if __name__ == "__main__":
    os.environ["SAGEMAKER_USER_CONFIG_OVERRIDE"] = os.getcwd()

    mlflow_arn = os.environ['MLFLOW_TRACKING_ARN']
    local_mode = os.getenv('LOCAL_MODE', False)
    role=get_execution_role()

    bucket_name = Session().default_bucket()
    project_prefix= "amzn"
    pipeline_name = f"{project_prefix}-sm-btd-pipeline"
    model_package_group_name = f"{project_prefix}-sm-btd-model-package-group"
    model_approval_status = "PendingManualApproval"
    experiment_name = pipeline_name
    run_name = ExecutionVariables.PIPELINE_EXECUTION_ID

    
    
    eta_parameter = ParameterFloat(
        name="eta", default_value=0.3
    )
    max_depth_parameter = ParameterInteger(
        name="max_depth", default_value=8
    )
    deploy_model_parameter = ParameterBoolean(
        name="deploy_model", default_value=True
    )
    
    input_data_s3_uri = download_data_and_upload_to_s3(bucket_name)    
    
    steps=create_steps(role, input_data_s3_uri, project_prefix, bucket_name, 
                       model_package_group_name, model_approval_status,
                       eta_parameter, max_depth_parameter, deploy_model_parameter, pipeline_name, run_name, mlflow_arn)

    local_pipeline_session = LocalPipelineSession()

    more_params = {}
    if local_mode:
        more_params["sagemaker_session"] = local_pipeline_session 
    
    pipeline = Pipeline(
        name=pipeline_name,
        parameters=[deploy_model_parameter, eta_parameter, max_depth_parameter],
        steps=steps,
        pipeline_definition_config=PipelineDefinitionConfig(use_custom_job_prefix=True),        
        **more_params
    )

    pipeline.upsert(role_arn=role)
    pipeline.start()
