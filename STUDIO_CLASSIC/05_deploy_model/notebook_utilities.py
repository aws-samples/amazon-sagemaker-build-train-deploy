import boto3

def get_latest_training_job_name(base_job_name):
    client = boto3.client('sagemaker')
    response = client.list_training_jobs(NameContains=base_job_name, SortBy='CreationTime', 
                                         SortOrder='Descending', StatusEquals='Completed')
    if len(response['TrainingJobSummaries']) > 0 :
        return response['TrainingJobSummaries'][0]['TrainingJobName']
    else:
        raise Exception('Training job not found.')

def get_training_job_s3_model_artifacts(job_name):
    client = boto3.client('sagemaker')
    response = client.describe_training_job(TrainingJobName=job_name)
    s3_model_artifacts = response['ModelArtifacts']['S3ModelArtifacts']
    return s3_model_artifacts
