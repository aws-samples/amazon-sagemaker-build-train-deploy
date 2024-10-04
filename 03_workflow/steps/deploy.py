import boto3
from sagemaker.model import ModelPackage
from sagemaker.utils import unique_name_from_base
import mlflow

def deploy(role, project_prefix, model_package_arn, deploy_model, experiment_name="main_experiment", run_id="run-01"):

    # Enable autologging in MLflow
    mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_ARN'])    
    mlflow.set_experiment(experiment_name)
    with mlflow.start_run(run_id=run_id) as run:        
        with mlflow.start_run(run_name="Deploy", nested=True):    
            mlflow.autolog()
            if deploy_model:
                sagemaker_client = boto3.client("sagemaker")
            
                response = sagemaker_client.update_model_package(
                    ModelPackageArn=model_package_arn,
                    ModelApprovalStatus='Approved',
                    ApprovalDescription='Auto-approved via SageMaker Pipelines')
            
                model_package = ModelPackage(
                    role = role,
                    model_package_arn = model_package_arn)
        
                endpoint_name = unique_name_from_base(f"{project_prefix}-sm-btd-endpoint")
                
                model_package.deploy(initial_instance_count=1,
                                     instance_type="ml.c5.xlarge",
                                     endpoint_name=endpoint_name)
            else:
                print("Skipped deploy model step based on parameter configuration.")
