import os
import time
import boto3
import sagemaker

from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.sklearn import SKLearnModel
from sagemaker.inputs import TrainingInput
from sagemaker.xgboost import XGBoost
from sagemaker.xgboost import XGBoostModel
from sagemaker.pipeline import PipelineModel
from sagemaker.workflow.parameters import (
    ParameterInteger,
    ParameterString,
)
from sagemaker.workflow.steps import (
    ProcessingStep,
    TrainingStep
)
from sagemaker.workflow.step_collections import RegisterModel
from sagemaker.workflow.pipeline import Pipeline

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

def get_sagemaker_client(region):
     boto_session = boto3.Session(region_name=region)
     sagemaker_client = boto_session.client("sagemaker")
     return sagemaker_client

def get_pipeline_custom_tags(new_tags, region, sagemaker_project_arn=None):
    try:
        sm_client = get_sagemaker_client(region)
        response = sm_client.list_tags(
            ResourceArn=sagemaker_project_arn)
        project_tags = response["Tags"]
        for project_tag in project_tags:
            new_tags.append(project_tag)
    except Exception as e:
        print(f"Error getting project tags: {e}")
    return new_tags

def get_session(region, default_bucket):
    boto_session = boto3.Session(region_name=region)

    sagemaker_client = boto_session.client("sagemaker")
    runtime_client = boto_session.client("sagemaker-runtime")
    return sagemaker.session.Session(
        boto_session=boto_session,
        sagemaker_client=sagemaker_client,
        sagemaker_runtime_client=runtime_client,
        default_bucket=default_bucket,
    )

def get_pipeline(region,
                 sagemaker_project_arn=None,
                 role=None,
                 default_bucket='',
                 pipeline_name='end-to-end-ml-sagemaker-pipeline',
                 model_package_group_name='end-to-end-ml-sm-model-package-group',
                 base_job_prefix='endtoendmlsm') -> Pipeline:
    """
    Gets the SM Pipeline.

    :param role: The execution role.
    :param bucket_name: The bucket where pipeline artifacts are stored.
    :param prefix: The prefix where pipeline artifacts are stored.
    :return: A Pipeline instance.
    """

    bucket_name = default_bucket
    prefix = 'endtoendmlsm'
    sagemaker_session = get_session(region, bucket_name)
    
    # ---------------------
    # Processing parameters
    # ---------------------
    # The path to the raw data.
    raw_data_path = 's3://gianpo-public/endtoendml/data/raw/predmain_raw_data_header.csv'.format(bucket_name, prefix)
    raw_data_path_param = ParameterString(name="raw_data_path", default_value=raw_data_path)
    # The output path to the training data.
    train_data_path = 's3://{0}/{1}/data/preprocessed/train/'.format(bucket_name, prefix)
    train_data_path_param = ParameterString(name="train_data_path", default_value=train_data_path)
    # The output path to the validation data.
    val_data_path = 's3://{0}/{1}/data/preprocessed/val/'.format(bucket_name, prefix)
    val_data_path_param = ParameterString(name="val_data_path", default_value=val_data_path)
    # The output path to the featurizer model.
    model_path = 's3://{0}/{1}/output/sklearn/'.format(bucket_name, prefix)
    model_path_param = ParameterString(name="model_path", default_value=model_path)
    # The instance type for the processing job.
    processing_instance_type_param = ParameterString(name="processing_instance_type", default_value='ml.m5.large')
    # The instance count for the processing job.
    processing_instance_count_param = ParameterInteger(name="processing_instance_count", default_value=1)
    # The train/test split ration parameter.
    train_test_split_ratio_param = ParameterString(name="train_test_split_ratio", default_value='0.2')
    # -------------------
    # Training parameters
    # -------------------
    # XGB hyperparameters.
    max_depth_param = ParameterString(name="max_depth", default_value='3')
    eta_param = ParameterString(name="eta", default_value='0.1')
    gamma_param = ParameterString(name="gamma", default_value='0')
    min_child_weight_param = ParameterString(name="min_child_weight", default_value='1')
    objective_param = ParameterString(name="objective", default_value='binary:logistic')
    num_round_param = ParameterString(name="num_round", default_value='10')
    eval_metric_param = ParameterString(name="eval_metric", default_value='auc')
    # The instance type for the training job.
    training_instance_type_param = ParameterString(name="training_instance_type", default_value='ml.m5.xlarge')
    # The instance count for the training job.
    training_instance_count_param = ParameterInteger(name="training_instance_count", default_value=1)
    # The training output path for the model.
    output_path = 's3://{0}/{1}/output/'.format(bucket_name, prefix)
    output_path_param = ParameterString(name="output_path", default_value=output_path)
    # --------------------------
    # Register model parameters
    # --------------------------
    # The default instance type for deployment.
    deploy_instance_type_param = ParameterString(name="deploy_instance_type", default_value='ml.m5.2xlarge')
    # The approval status for models added to the registry.
    model_approval_status_param = ParameterString(name="model_approval_status", default_value='PendingManualApproval')
    # --------------------------
    # Processing Step
    # --------------------------
    sklearn_processor = SKLearnProcessor(role=role,
                                         instance_type=processing_instance_type_param,
                                         instance_count=processing_instance_count_param,
                                         framework_version='0.20.0')
    inputs = [ProcessingInput(input_name='raw_data',
                              source=raw_data_path_param, destination='/opt/ml/processing/input')]
    outputs = [ProcessingOutput(output_name='train_data',
                                source='/opt/ml/processing/train', destination=train_data_path_param),
               ProcessingOutput(output_name='val_data',
                                source='/opt/ml/processing/val', destination=val_data_path_param),
               ProcessingOutput(output_name='model',
                                source='/opt/ml/processing/model', destination=model_path_param)]
    code_path = os.path.join(BASE_DIR, 'dataprep/preprocess.py')
    processing_step = ProcessingStep(
        name='Processing',
        code=code_path,
        processor=sklearn_processor,
        inputs=inputs,
        outputs=outputs,
        job_arguments=['--train-test-split-ratio', train_test_split_ratio_param]
    )
    # --------------------------
    # Training Step
    # --------------------------
    hyperparameters = {
        "max_depth": max_depth_param,
        "eta": eta_param,
        "gamma": gamma_param,
        "min_child_weight": min_child_weight_param,
        "silent": 0,
        "objective": objective_param,
        "num_round": num_round_param,
        "eval_metric": eval_metric_param
    }
    entry_point = 'train.py'
    source_dir = os.path.join(BASE_DIR, 'train/')
    code_location = 's3://{0}/{1}/code'.format(bucket_name, prefix)
    estimator = XGBoost(
        entry_point=entry_point,
        source_dir=source_dir,
        output_path=output_path_param,
        code_location=code_location,
        hyperparameters=hyperparameters,
        instance_type=training_instance_type_param,
        instance_count=training_instance_count_param,
        framework_version="0.90-2",
        py_version="py3",
        role=role
    )
    training_step = TrainingStep(
        name='Training',
        estimator=estimator,
        inputs={
            'train': TrainingInput(
                s3_data=processing_step.properties.ProcessingOutputConfig.Outputs[
                    'train_data'
                ].S3Output.S3Uri,
                content_type='text/csv'
            ),
            'validation': TrainingInput(
                s3_data=processing_step.properties.ProcessingOutputConfig.Outputs[
                    'val_data'
                ].S3Output.S3Uri,
                content_type='text/csv'
            )
        }
    )
    # --------------------------
    # Register Model Step
    # --------------------------
    code_location = 's3://{0}/{1}/code'.format(bucket_name, prefix)
    sklearn_model = SKLearnModel(name='end-to-end-ml-sm-skl-model-{0}'.format(str(int(time.time()))),
                                 model_data=processing_step.properties.ProcessingOutputConfig.Outputs[
                                     'model'].S3Output.S3Uri,
                                 entry_point='inference.py',
                                 source_dir=os.path.join(BASE_DIR, 'deploy/sklearn/'),
                                 code_location=code_location,
                                 role=role,
                                 sagemaker_session=sagemaker_session,
                                 framework_version='0.20.0',
                                 py_version='py3')
    code_location = 's3://{0}/{1}/code'.format(bucket_name, prefix)
    xgboost_model = XGBoostModel(name='end-to-end-ml-sm-xgb-model-{0}'.format(str(int(time.time()))),
                                 model_data=training_step.properties.ModelArtifacts.S3ModelArtifacts,
                                 entry_point='inference.py',
                                 source_dir=os.path.join(BASE_DIR, 'deploy/xgboost/'),
                                 code_location=code_location,
                                 framework_version='0.90-2',
                                 py_version='py3',
                                 role=role,
                                 sagemaker_session=sagemaker_session)
    pipeline_model_name = 'end-to-end-ml-sm-xgb-skl-pipeline-{0}'.format(str(int(time.time())))
    pipeline_model = PipelineModel(
        name=pipeline_model_name,
        role=role,
        models=[
            sklearn_model,
            xgboost_model],
        sagemaker_session=sagemaker_session)

    register_model_step = RegisterModel(
        name='RegisterModel',
        content_types=['text/csv'],
        response_types=['application/json', 'text/csv'],
        inference_instances=[deploy_instance_type_param, 'ml.m5.large'],
        transform_instances=['ml.c5.4xlarge'],
        model_package_group_name=model_package_group_name,
        approval_status=model_approval_status_param,
        model=pipeline_model
    )
    # --------------------------
    # Pipeline
    # --------------------------

    pipeline = Pipeline(
        name=pipeline_name,
        parameters=[
            raw_data_path_param,
            train_data_path_param,
            val_data_path_param,
            model_path_param,
            processing_instance_type_param,
            processing_instance_count_param,
            train_test_split_ratio_param,
            max_depth_param,
            eta_param,
            gamma_param,
            min_child_weight_param,
            objective_param,
            num_round_param,
            eval_metric_param,
            training_instance_type_param,
            training_instance_count_param,
            output_path_param,
            deploy_instance_type_param,
            model_approval_status_param
        ],
        steps=[processing_step, training_step, register_model_step],
        sagemaker_session=sagemaker_session,
    )
    response = pipeline.upsert(role_arn=role)
    print(response["PipelineArn"])
    return pipeline


def run_pipeline(pipeline: Pipeline, parameters: dict) -> str:
    """
    Runs the SM Pipeline.
    :param pipeline: The SM Pipeline instance.
    :param parameters: The pipeline execution parameters.
    :return: The ARN of the registered model package.
    """

    execution = pipeline.start(parameters)
    execution.wait()

    # Let's check the model package has been registered
    steps = execution.list_steps()
    register_model_step = next(s for s in steps if s['StepName'] == 'RegisterModel')
    model_package_arn = register_model_step['Metadata']['RegisterModel']['Arn']

    return model_package_arn


if __name__ == "__main__":

    execution_role = sagemaker.get_execution_role()
    session = sagemaker.Session()
    bucket = session.default_bucket()
    
    boto_session = boto3.session.Session()
    region = boto_session.region_name

    # Build pipeline.
    end_to_end_pipeline = get_pipeline(region, None, execution_role, bucket)

    # Set parameters.
    execution_parameters = {
        'train_test_split_ratio': '0.2'
    }

    # Run pipeline
    model_package_version_arn = run_pipeline(end_to_end_pipeline, execution_parameters)
    print(model_package_version_arn)
