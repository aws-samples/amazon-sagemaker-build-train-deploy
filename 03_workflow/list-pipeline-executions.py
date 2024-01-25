import boto3

def describe_last_sagemaker_pipeline():
    sagemaker_client = boto3.client("sagemaker")
    response = sagemaker_client.list_pipeline_executions(PipelineName="sagemaker-btd-pipeline")
    return sorted(response["PipelineExecutionSummaries"], reverse=True, key=lambda k: k["StartTime"])[0]

def list_execution_execution_steps(pipelineExecutionArn):
    sagemaker_client = boto3.client("sagemaker")
    response = sagemaker_client.list_pipeline_execution_steps(PipelineExecutionArn=pipelineExecutionArn)
    return response["PipelineExecutionSteps"]

last_pipeline_execution = describe_last_sagemaker_pipeline()
pipeline_execution_steps = list_execution_execution_steps(last_pipeline_execution["PipelineExecutionArn"])

print(f'Pipeline Execution ARN: {last_pipeline_execution["PipelineExecutionArn"]}')
print(f'Execution Status: {last_pipeline_execution["PipelineExecutionStatus"]}')
print(f'Start Time: {last_pipeline_execution["StartTime"]}')
print("---------------")
print("---------------")

for step in pipeline_execution_steps:
    print(f'Step name: {step["StepName"]}')
    print(f'Step status: {step["StepStatus"]}')
    print(f'Start time: {step["StartTime"]:"%d/%m/%Y %H:%M:%S"}')
    print(f'End time: {step["EndTime"]:"%d/%m/%Y %H:%M:%S"}')
    print("-----")