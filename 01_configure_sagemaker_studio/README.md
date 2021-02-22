#Amazon SageMaker Hands-On Workshop

# Workshop Instructions
_Note:  This workshop will create an ephemeral AWS acccount for each attendee.  This ephemeral account is not accessible after the workshop.  You can, of course, clone this GitHub repo and reproduce the entire workshop in your own AWS Account._

## 0. Logout of All AWS Consoles Across All Browser Tabs
If you do not logout of existing AWS Consoles, things will not work properly.

![AWS Account Logout](img/aws-logout.png)

_Please logout of all AWS Console sessions in all browser tabs._

## 1. Login to the Workshop Portal (aka Event Engine). 
Using the hash code you got by email, paste the team-hash-login to a new browser window. 

Choose the Accept Terms & Login. 

![Event Engine Terms and Conditions](img/event-engine-terms.png)

![Event Engine Dashboard](img/event-engine-dashboard.png)

## 2. Login to the **AWS Console**

![Event Engine AWS Console](img/event-engine-aws-console.png)

Take the defaults and click on **Open AWS Console**. This will open AWS Console in a new browser tab.

If you see this message, you need to logout from any previously used AWS accounts.

![AWS Account Logout](img/aws-logout.png)

_Please logout of all AWS Console sessions in all browser tabs._

Double-check that your account name is similar to `TeamRole/MasterKey` as follows:

![IAM Role](img/teamrole-masterkey.png)

If not, please logout of your AWS Console in all browser tabs and re-run the steps above!

## 3. Launch SageMaker Studio

Open the [AWS Management Console](https://console.aws.amazon.com/console/home)

**Note:** This workshop has been tested on the US East (N. Virginia) (us-east-1) region. Make sure that you see **N.Virginia** on the top right hand corner of your AWS Management Console. If you see a different region, click the dropdown menu and select US East (N. Virginia).

In the AWS Console search bar, type `SageMaker` and select `Amazon SageMaker` to open the service console.

![SageMaker Console](img/setup_aws_console.png). 

Now, open SageMaker Studio:

![SageMaker Studio](img/open_sm_studio_1.png)

and click "Open Studio": (the first time you open SageMaker Studio, this step will take a few minutes to launch)

![SageMaker Studio](img/open_sm_studio_2.png)


## 4. Clone the GitHub Repo
Click the Git icon (1 in the picture) and then select `Clone a repository` (step 2).

![Clone the repository](img/smstudio_clone_repo_steps.jpg)

Type in the URL of this repository (https://github.com/shneydor/amazon-sagemaker-build-train-deploy.git) and click `Clone`.

![Clone the repository](img/clone_a_repo.png)



## 5. Start the Workshop!

In the File Browser, click `amazon-sagemaker-build-train-deploy` and open the folder `02_data_exploration_and_feature_eng`

Then, open the `02_data_exploration_and_feature_eng.ipynb` Jupyter notebook.

![Open step 2 folder](img/smstudio_open_notebook.jpg)

![Open step 2 notebook](img/smstudio_open_notebook2.jpg)


Select the "Python 3 Data Science" Kernel by clicking "No Kernel" at the bottom. Then wait until the kernel has started, and start the workshop!

![kernel_setup1](img/kernel_choice_1.png)
![kernel_setup2](img/kernel_choice_2.png)
![kernel_setup4](img/kernel_choice_4.png)

