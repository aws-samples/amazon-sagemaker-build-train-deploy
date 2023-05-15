import boto3
import yaml

networking_stack = ""
sagemaker_stack = ""

cf_client = boto3.client('cloudformation')

def set_networking_defaults(defaults):
    response = cf_client.describe_stacks(StackName=networking_stack)

    outputs = response["Stacks"][0]["Outputs"]
    for output in outputs:
        keyName = output["OutputKey"]

        if "SageMakerSubnet" in keyName:
            defaults["SageMaker"]["ProcessingJob"]["NetworkConfig"]["VpcConfig"]["Subnets"].append(output["OutputValue"])
            defaults["SageMaker"]["TrainingJob"]["VpcConfig"]["Subnets"].append(output["OutputValue"])
            defaults["SageMaker"]["Model"]["VpcConfig"]["Subnets"].append(output["OutputValue"])
        elif "SageMakerSecurityGroup" in keyName:
            defaults["SageMaker"]["ProcessingJob"]["NetworkConfig"]["VpcConfig"]["SecurityGroupIds"].append(output["OutputValue"])
            defaults["SageMaker"]["TrainingJob"]["VpcConfig"]["SecurityGroupIds"].append(output["OutputValue"])
            defaults["SageMaker"]["Model"]["VpcConfig"]["SecurityGroupIds"].append(output["OutputValue"])

    if len(defaults["SageMaker"]["ProcessingJob"]["NetworkConfig"]["VpcConfig"]["Subnets"]) == 0:
        if len(defaults["SageMaker"]["ProcessingJob"]["NetworkConfig"]["VpcConfig"]["SecurityGroupIds"]) == 0:
            del defaults["SageMaker"]["ProcessingJob"]["NetworkConfig"]["VpcConfig"]
        else:
            del defaults["SageMaker"]["ProcessingJob"]["NetworkConfig"]["VpcConfig"]["Subnets"]
    elif len(defaults["SageMaker"]["ProcessingJob"]["NetworkConfig"]["VpcConfig"]["SecurityGroupIds"]) == 0:
        del defaults["SageMaker"]["ProcessingJob"]["NetworkConfig"]["VpcConfig"]["SecurityGroupIds"]

    if len(defaults["SageMaker"]["TrainingJob"]["VpcConfig"]["Subnets"]) == 0:
        if len(defaults["SageMaker"]["TrainingJob"]["VpcConfig"]["SecurityGroupIds"]) == 0:
            del defaults["SageMaker"]["TrainingJob"]["VpcConfig"]
        else:
            del defaults["SageMaker"]["TrainingJob"]["VpcConfig"]["Subnets"]
    elif len(defaults["SageMaker"]["TrainingJob"]["VpcConfig"]["SecurityGroupIds"]) == 0:
        del defaults["SageMaker"]["TrainingJob"]["VpcConfig"]["SecurityGroupIds"]

    if len(defaults["SageMaker"]["Model"]["VpcConfig"]["Subnets"]) < 0:
        if len(defaults["SageMaker"]["Model"]["VpcConfig"]["SecurityGroupIds"]) == 0:
            del defaults["SageMaker"]["Model"]["VpcConfig"]
        else:
            del defaults["SageMaker"]["Model"]["VpcConfig"]["Subnets"]
    elif len(defaults["SageMaker"]["Model"]["VpcConfig"]["SecurityGroupIds"]) == 0:
        del defaults["SageMaker"]["Model"]["VpcConfig"]["SecurityGroupIds"]

    return defaults

def set_sagemaker_defaults(defaults):
    response = cf_client.describe_stacks(StackName=sagemaker_stack)

    outputs = response["Stacks"][0]["Outputs"]
    for output in outputs:
        keyName = output["OutputKey"]

        if "KMSKey" in keyName:
            defaults["SageMaker"]["ProcessingJob"]["ProcessingOutputConfig"]["KmsKeyId"] = output["OutputValue"]
            defaults["SageMaker"]["TrainingJob"]["OutputDataConfig"]["KmsKeyId"] = output["OutputValue"]
        elif "SageMakerExecutionRoleArn" in keyName:
            defaults["SageMaker"]["ProcessingJob"]["RoleArn"] = output["OutputValue"]
            defaults["SageMaker"]["TrainingJob"]["RoleArn"] = output["OutputValue"]
            defaults["SageMaker"]["Model"]["ExecutionRoleArn"] = output["OutputValue"]

    if "KmsKeyId" not in defaults["SageMaker"]["ProcessingJob"]["ProcessingOutputConfig"]:
        del defaults["SageMaker"]["ProcessingJob"]["ProcessingOutputConfig"]

    if "KmsKeyId" not in defaults["SageMaker"]["TrainingJob"]["OutputDataConfig"]:
        del defaults["SageMaker"]["TrainingJob"]["OutputDataConfig"]

    return defaults

def main():
    defaults = {
        "SchemaVersion": "1.0",
        "SageMaker": {
            "ProcessingJob": {
                "NetworkConfig": {
                    "EnableNetworkIsolation": False,
                    "VpcConfig": {
                        "SecurityGroupIds": [],
                        "Subnets": []
                    }
                },
                "ProcessingOutputConfig": {}
            },
            "TrainingJob": {
                "EnableNetworkIsolation": False,
                "VpcConfig": {
                    "SecurityGroupIds": [],
                    "Subnets": []
                },
                "OutputDataConfig": {}
            },
            "Model": {
                "EnableNetworkIsolation": False,
                "VpcConfig": {
                    "SecurityGroupIds": [],
                    "Subnets": []
                }
            }
        }
    }

    defaults = set_networking_defaults(defaults)
    defaults = set_sagemaker_defaults(defaults)

    f = open('user-configs.yaml', 'w+')
    yaml.dump(defaults, f, sort_keys=False)

    f = open('admin-configs.yaml', 'w+')
    yaml.dump(defaults, f, sort_keys=False)

if __name__ == "__main__":
    main()
