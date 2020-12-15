// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. // SPDX-License-Identifier: CC-BY-SA-4.0

# Create a managed Jupyter Notebook instance with Amazon SageMaker

## Overview

Amazon SageMaker is a fully-managed service that enables developers and data scientists to quickly and easily build, train, and deploy machine learning models at any scale. Amazon SageMaker removes all the barriers that typically slow down developers who want to use machine learning.

Machine learning often feels a lot harder than it should be to most developers because the process to build and train models, and then deploy them into production is too complicated and too slow. First, you need to collect and prepare your training data to discover which elements of your data set are important. Then, you need to select which algorithm and framework you’ll use. After deciding on your approach, you need to teach the model how to make predictions by training, which requires a lot of compute. Then, you need to tune the model so it delivers the best possible predictions, which is often a tedious and manual effort. After you’ve developed a fully trained model, you need to integrate the model with your application and deploy this application on infrastructure that will scale. All of this takes a lot of specialized expertise, access to large amounts of compute and storage, and a lot of time to experiment and optimize every part of the process. In the end, it's not a surprise that the whole thing feels out of reach for most developers.

Amazon SageMaker removes the complexity that holds back developer success with each of these steps. Amazon SageMaker includes modules that can be used together or independently to build, train, and deploy your machine learning models.

In this section, we will walk you through creating a fully-managed Jupyter Notebook instance with Amazon SageMaker, that will be used to execute our experimentation and build the Machine Learning model.

## Create a managed Jupyter Notebook instance
An **Amazon SageMaker notebook instance** is a fully managed ML compute instance running the <a href="http://jupyter.org/">**Jupyter Notebook**</a> application. Amazon SageMaker manages creating the instance and related resources. 

1. In the AWS Management Console, click on Services, type “SageMaker” and press enter.
	
	<img src="images/search_sagemaker.png" alt="Search SageMaker" width="700px" />

2. You’ll be placed in the Amazon SageMaker dashboard. Click on **Notebook instances** either in the landing page or in the left menu.
	
	<img src="images/sagemaker_dashboard.png" alt="SageMaker dashboard" width="700px" />
	
3. Once in the Notebook instances screen, click on the top-righ button **Create notebook instance**.

	<img src="images/notebook_instances_screen.png" alt="Notebook Instances screen" width="700px" />
 
4. In the **Create notebook instance** screen

	<img src="images/create_notebook_instance_screen.png" alt="Create Notebook Instance screen" width="700px" />

	1. Give the Notebook Instance a name like _endtoendml-nb-**[your-initials]**_

	2. Choose **ml.t2.medium** as **Notebook instance type**
	3. In the **IAM role** dropdown list you need to select an AWS IAM Role that is configured with security policies allowing access to Amazon SageMaker, AWS Glue and Amazon S3. The role has been pre-configured for you, so you just need to select **_AmazonSageMaker-ExecutionRole-endtoendml_** in the dropdown list.

	4. Keep **No VPC** selected in the **VPC** dropdown list
	5. Keep **No configuration** selected in the **Lifecycle configuration** dropdown list
	6. Keep **No Custom Encryption** selected in the **Encryption key** dropdown list
	7. Finally, click on **Create notebook instance**

4. You will be redirected to the **Notebook instances** screen and you will see a new notebook instance in _Pending_ state.

	<img src="images/notebook_instances_pending.png" alt="Notebook instances pending" width="700px" />
	
	Wait until the notebook instance is status is _In Service_ and then click on the **Open** button to be redirected to Jupyter.

	<img src="images/notebook_instances_in_service.png" alt="Notebook instances in service" width="700px" />
	
	<img src="images/jupyter_screen.png" alt="Jupyter screen" width="700px" />

## Download workshop code to the notebook instance

All the code of this workshop is pre-implemented and available for download from GitHub.

As a consequence, in this section we will clone the GitHub repository into the Amazon SageMaker notebook instance and access the Jupyter Notebooks to build our model.

1. Click on **New > Terminal** in the right-hand side of the Jupyter interface
	
	<img src="images/jupyter_new_terminal.png" alt="Jupyter New Terminal screen" width="700px" />

	This will open a terminal window in the Jupyter interface
	
	<img src="images/jupyter_terminal.png" alt="Jupyter Terminal screen" width="700px" />

2. Execute the following commands in the terminal

	```bash
	cd SageMaker/
	git clone https://github.com/aws-samples/amazon-sagemaker-build-train-deploy
	```
3. When the clone operation completes, close the terminal window and return to the Jupyter landing page. The folder **amazon-sagemaker-build-train-deploy** will appear automatically (if not, you can hit the **Refresh** button)

	<img src="images/jupyter_cloned_workshop_screen.png" alt="Jupyter Cloned Workshop Screen" width="700px" />
	
4. Browse to the folder **02\_data\_exploration\_and\_feature\_eng** and open the file **02\_data\_exploration\_and\_feature\_eng.ipynb** to start the data exploration, preparation and feature engineering steps.

You can now proceed to <a href="../02_data_exploration_and_feature_eng/">Module 02</a>
