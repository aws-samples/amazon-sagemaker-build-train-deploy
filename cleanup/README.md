To make sure you do not incur additional charges after you complete the workshop, follow these steps to remove the resources you created.

### 1. Make note of the Amazon Resource Name (ARN) for the SageMaker Studio domain
You will need the full ARN of the SageMaker Studio domain in step 3.   
- Go to the CloudFormation console, select the second stack you created (named _endtoendml-workshop-sagemaker_ if you used the suggested name in the blog). 
- Go to the Output tab, copy the value of the output named `StudioDomainArn` and keep it somewhere safe.

### 2. Delete the SageMaker Endpoint and resources
Follow the steps to delete the [SageMaker inference endpoint and resources via the AWS console](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints-delete-resources.html).

### 3. Delete the SageMaker Studio and associated resources
- Go to the CloudFormation console.
- Locate the second stack you created (_endtoendml-workshop-sagemaker_ if you used the suggested name in the blog) and delete the stack.
- When the stack is deleted, move to the next step.

### 4. Remove the mount points (ENIs) for the EFS volume, ENI for the inference endpoint, and security groups created by SageMaker Studio
In this step, you will delete the resources that were automatically created when you created the SageMaker Studio domain, including the EFS mount points and security groups.

Perform the following steps on your local machine. Make sure you have set AWS credentials and profile in the your shell environment.

Make sure the dependencies are installed.

`python3 -m pip install --user -r requirements.txt`

Run `cleanup-efs.py`, passing in the the ARN of the SageMaker Studio domain as an argument.

`python3 cleanup.py --sagemaker-studio-domain [ARN for the SageMaker Studio domain from step 1]`

To prevent accidental data loss, the script does not delete the volume, so you should delete the volume yourself once you have made sure you do not need any data or code you might have created in SageMaker Studio. The script writes the File System ID for the EFS volume to the output. Make a note of the file system ID as you will need it in step 6.

### 5. Delete the VPC and other networking resources
You can now delete the VPC and its associated resources such as VPC endpoints and subnets. In the CloudFormation console, locate the first stack you created (_named endtoendml-workshop-networking_ if you used the suggested name) and delete it. If the stack fails to delete after a while, make sure you have completed step 4.

### 6. Delete the EFS volume
Once you have made sure you do not need the data in the EFS volume, go to the EFS console, locate the EFS volume using the file system ID you noted earlier, and delete it.