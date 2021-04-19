# Open Amazon SageMaker Studio and clone the repository

## Overview

Amazon SageMaker is a fully-managed service that enables developers and data scientists to quickly and easily build, train, and deploy machine learning models at any scale.

Amazon SageMaker removes the complexity that holds back developer success with each of these steps; indeed, it includes modules that can be used together or independently to build, train, and deploy your machine learning models.

In this section, we will walk you through accessing the AWS Console, Amazon SageMaker Studio, and cloning this repository for executiong next modules.

## Access the AWS Console

1. Sign into the **AWS Management Console** using the Event Engine dashboard at <a href="https://dashboard.eventengine.run" target="_blank">https://dashboard.eventengine.run</a> and **the hashcode provided by the workshop instructors**. [Or access it at <a href="https://console.aws.amazon.com/" target="_blank">https://console.aws.amazon.com/</a> if you are using your own AWS account].

	<img src="images/event_engine_login.png" alt="Event Engine login" width="500px" />
    
	<img src="images/event_engine_dashboard.png" alt="Event Engine dashboard" width="500px" />
    
	<img src="images/event_engine_console_login.png" alt="Event Engine console login" width="500px" />

2. In the upper-right corner of the AWS Management Console, confirm you are in the desired AWS region. For the instructions of these workshop we will assume using the **EU West (Ireland)** [eu-west-1], but feel free to change the region at your convenience.

	> The only constraints for changing AWS region are that we keep consistent the region settings for all services used and services are available in the selected region (please check in case you plan to execute this workshop in another AWS region).


## Open Amazon SageMaker Studio
Amazon SageMaker Studio has been pre-configured in the AWS Account. In this section we will open Studio and clone the repository.

1. In the AWS Management Console, search for "SageMaker" and select Amazon SageMaker in the results.
	
	<img src="images/aws_console_search_sm.png" alt="Search SageMaker" width="700px" />

2. You’ll be placed in the Amazon SageMaker dashboard. Click on **Amazon SageMaker Studio** in the left menu and then on the **Open Studio** button associated to the defaultuser.
	
	<img src="images/studio_console.png" alt="Studio dashboard" width="700px" />
	
3. Amazon SageMaker Studio will load (it can take a few minutes). Then you will be redirected to the Studio interface.

	<img src="images/studio_landing.png" alt="Studio interface" width="700px" />


## Clone the repository

1. In the **File** menu, choose **New >> Terminal**

	<img src="images/studio_new_terminal.png" alt="Studio New Terminal" width="700px" />

	This will open a terminal window in the Jupyter interface.

2. Execute the following commands in the terminal

	```bash
	git clone https://github.com/aws-samples/amazon-sagemaker-build-train-deploy.git
	```
    The repository will be cloned to your use home and will appear in the file browser panel as shown below:
    
    <img src="images/studio_clone_repo.png" alt="Studio clone repo" width="700px" />
	
3. Browse to the folder **02\_data\_exploration\_and\_feature\_eng** and open the file **02\_data\_exploration\_and\_feature\_eng.ipynb** to start the data exploration, preparation and feature engineering steps.

    <img src="images/studio_select_second_notebook.png" alt="Studio select second nb" width="700px" />
    
4. If a kernel is not automatically selected for your notebook, choose the kernel by clicking on the **Kernel** button on the top-right and them selecting the **Python 3 (Data Science)** kernel as shown below:

    <img src="images/studio_select_kernel_button.png" alt="Studio select kernel button" width="700px" />
    
    <img src="images/studio_select_kernel.png" alt="Studio select kernel" width="500px" />
