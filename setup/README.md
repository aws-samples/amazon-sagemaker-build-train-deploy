# Setup your AWS Account

> ⚠️ **Warning**: The following steps need to be executed **only** if you are going to use **your own AWS account** for the workshop. Please do not execute any action if an AWS account was provided by an AWS instructor.

## Prerequisites
If you are going to use your own AWS Account, we assume that you have **administrator privileges** in that account. If this is not the case, please double-check with your AWS system administrator before moving to next section.

## Create resources using AWS CloudFormation
Amazon SageMaker Studio allows you to configure networking in two modes:
- **Public internet only**: Non-EFS traffic goes through a SageMaker managed VPC, which allows internet access. Only traffic between the Domain and your Amazon EFS volume is through the specified VPC.
- **VPC only**: All SageMaker traffic is through the specified VPC and subnets. Internet access is disabled by default, but you can provide internet access using a NAT Gateway or a Transit Gateway.

For this workshop, we provide AWS CloudFormation templates for both modes in two separate folders: `public_internet_only_mode` and `vpc_only_mode`.

You will create the resources needed for the workshop using two CloudFormation templates:
- `01_networking.yaml` will create the core networking resources such as VPCs and subnets
- `02_sagemaker_studio.yaml`, will create the SageMaker Studio resources such as a SageMaker Studio domain, user profile, and applications.

### Create the core networking resources
In this section, we will create the networking resources. If you choose the `public_internet_only_mode` folder, the networking template will create a VPC, two public subnets, an Internet Gateway with the relevant route table and routes. If you choose the `vpc_only_mode` folder, the networking template will create two public and two private subnets, a NAT Gateway, and the appropriate route table and routes.

Please execute the following steps:

1. Sign into the [**AWS Management Console**](https://console.aws.amazon.com/)

2. In the upper-right corner of the AWS Management Console, confirm you are in the desired AWS region. For the instructions of these workshop we will use the **US East (N. Virginia)** [us-east-1].
   
	> You can use another region as long as the services we use for the workshop are available in the selected region. If you change the region, make sure you use the same region for all steps.

3. Open the [**AWS CloudFormation** console](https://console.aws.amazon.com/cloudformation) or choose the CloudFormation service in the menu.

4. On the AWS CloudFormation landing page, press the **Create stack** button.

	<img src="images/cloudformation_create_stack1_step_0.png" alt="Create CloudFormation stack" width="700px" />
	
5. On the **Create stack** screen, select **Template is ready** and **Upload a template file** as shown below. After selecting **Choose file**, choose `01_networking.yaml` from the relevant folder and press the **Next** button at the bottom of the screen.
	
	<img src="images/cloudformation_create_stack1_step_1.png" alt="CloudFormation create stack screen 1" width="700px" />
	
6. On the **Specify stack details** screen, input a stack name like _endtoendml-workshop-networking_ and press **Next**.
	
	<img src="images/cloudformation_create_stack1_step_2.png" alt="CloudFormation create stack screen 2" width="700px" />
	
7. Don't make any changes on the **Configure stack options** screen and just press **Next**.
   
8. On the final **Review endtoendml-workshop-networking** screen, scroll to the bottom without making any changes, and click the **Create Stack** button.
	
9.  AWS CloudFormation will start creating the AWS resources defined in the template. You can monitor the progress from the **Stack detail** screen. Wait a few seconds until the screen reports that the stack creation is completed successfully.

	<img src="images/cloudformation_check_status_stack1.png" alt="CloudFormation check stack creation" width="700px" />


### Create the Amazon SageMaker Studio resources
In this section, we will create the Amazon SageMaker Studio domain and a user profile required to run this workshop. More specifically, we are going to create the following resources:

- An Amazon SageMaker Studio domain
- An Amazon SageMaker Studio user profile
- A JupyterServer app for the user profile
- A Data Science app for the user profile
- The IAM roles required to run the workshop

Please execute the following steps:

1. On the AWS CloudFormation landing page, press the **Create stack** button.
	
2. On the **Create stack** screen, select **Template is ready** and **Upload a template file** as shown below. After selecting **Choose file**, choose `02_sagemaker_studio.yaml` from the relevant folder and press the **Next** button at the bottom of the screen.
	
	<img src="images/cloudformation_create_stack2_step_1.png" alt="CloudFormation create stack screen 1" width="700px" />
	
3. On the **Specify stack details** screen, input a stack name like _endtoendml-workshop-sagemaker_. Enter the name of the stack you created earlier (_endtoendml-workshop-networking_ if you used the value we suggested) and enter a user profile name or accept the default value. Finally, press **Next**.
	
	<img src="images/cloudformation_create_stack2_step_2.png" alt="CloudFormation create stack screen 2" width="700px" />
	
4. Don't make any changes on the **Configure stack options** screen and just press **Next**.
   
5. On the final **Review endtoendml-workshop-sagemaker** screen, scroll to the bottom, check the checkbox informing that AWS Cloudformation might create IAM resources with custom names and click the **Create Stack** button.

	<img src="images/cloudformation_create_stack2_step_4.png" alt="CloudFormation create stack screen 4" width="700px" />
   
6.  AWS CloudFormation will start creating the AWS resources defined in the template. You can monitor the progress from the **Stack detail** screen. Wait a few seconds until the screen reports that the stack creation is completed successfully.

	<img src="images/cloudformation_check_status_stack2.png" alt="CloudFormation check stack creation" width="700px" />
	

## Proceed to the first module

1.  Start the workshop from <a href="../01_configure_sagemaker_studio/">**Module 01**</a>.