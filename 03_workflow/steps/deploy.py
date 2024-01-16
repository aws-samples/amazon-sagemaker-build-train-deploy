import boto3
from sagemaker.model import ModelPackage
from sagemaker.utils import unique_name_from_base

def deploy(role, model_package_arn, deploy_model):

    if deploy_model:
        sagemaker_client = boto3.client("sagemaker")
    
        response = sagemaker_client.update_model_package(
            ModelPackageArn=model_package_arn,
            ModelApprovalStatus='Approved',
            ApprovalDescription='Auto-approved via SageMaker Pipelines')
    
        model_package = ModelPackage(
            role = role,
            model_package_arn = model_package_arn)

        endpoint_name = unique_name_from_base("sagemaker-btd-endpoint")
        
        model_package.deploy(initial_instance_count=1,
                             instance_type="ml.c5.xlarge",
                             endpoint_name=endpoint_name)
    else:
        print("Skipped deploy model step based on parameter configuration.")
