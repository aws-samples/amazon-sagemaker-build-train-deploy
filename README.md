# Scale complete ML development with Amazon SageMaker Studio

In this workshop, you will go through the steps required to build a machine learning application on AWS using Amazon SageMaker. 

You will learn how to start experimentation in the SageMaker Studio environment using a familiar JupyterLab notebook experience and run your local code as a SageMaker training job using the remote function feature. You will also learn how to use SageMaker Studio's Code Editor, which is based on Visual Studio Code – Open Source (Code-OSS), to deploy the model into an endpoint and build an end to end pipeline. You wull also learn how to build an HTTP endpoint using AWS Lambda and Amazon API Gateway to serve inference requests from a web client.

## The Machine Learning Process

The Machine Learning process is an iterative process consisting of several steps:

- Identifying a business problem and the related machine learning problem
- Data ingestion, integration and preparation
- Data visualization and analysis, feature engineering, model training and model evaluation
- Model deployment, model monitoring and debugging

These steps are usually repeated multiple times to better meet business goals after the source data changes or performance of the model drops, for example.

The following diagram shows how the process works:

<img src="images/ml_process.png" alt="ML Process" />

After you deploy a model, you can integrate it with your own application to provide insights to the end users.

## Amazon SageMaker

Amazon SageMaker is a fully-managed service that enables developers and data scientists to quickly and easily build, train, and deploy machine learning models at any scale.

Amazon SageMaker removes the complexity that holds back developer success with each of these steps; indeed, it includes modules that can be used together or independently to build, train, and deploy your machine learning models.


## The Machine Learning task

You will use the <a href="https://archive.ics.uci.edu/ml/datasets/AI4I+2020+Predictive+Maintenance+Dataset">AI4I 2020 Predictive Maintenance Dataset</a> from the UCI Machine Learning Repository. This synthetic dataset reflects real predictive maintenance data encountered in industry.

The dataset consists of 10,000 records and 14 features, representing some measurements that have been collected on the machinery, plus the indication of failure, if any. This is a basic dataset that oversimplifies the Predictive Maintenance task. However, it keeps this workshop easy to follow while being a good representative of the various steps of the machine learning workflow.

Your goal is to build a simple machine learning model that predicts whether a piece of machinery is going to fail.

Following is an excerpt from the dataset:

|UDI|Product ID|Type|Air temperature [K]|Process temperature [K]|...|Machine failure|
|-------|-------|-------|-------|-------|-------|-------|
|1|M14860|M|298.1|308.6|...|0|
|2|L47181|L|298.2|308.7|...|0|
|3|L47182|L|298.1|308.5|...|0|
|51|L47230|L|298.9|309.1|...|1|

The binary (0 or 1) nature of the target variable, **Machine failure**, suggests you are solving a binary classification problem. In this workshop, you will build a regression model, which will predict a continuous in the range [0,1). Using a regression model to solve a binary classification problem is a common approach. The predicted regression score indicates the system’s certainty that the given observation belongs to the positive class. To make the decision about whether the observation should be classified as positive or negative, as a consumer of this score, you can interpret the score by picking a classification threshold (cut-off) and compare the score against it. Any observations with scores higher than the threshold are then predicted as the positive class and scores lower than the threshold are predicted as the negative class. To learn more about this approach, read https://docs.aws.amazon.com/machine-learning/latest/dg/binary-classification.html.


## Solution Architecture

This diagram shows what you will be building in this workshop:
<img src="images/architecture.png" alt="Architecture" />


## Modules

This workshops consists of six modules:

- **Module 0**: Access the AWS Console and clone the GitHub repository.
- **Module 1**: Use a JupyterLab space in SageMaker Studio to perform experimentation and feature engineering, and build and train a regression model using XGBoost. The model will predict whether the machinery is going to fail.
- **Module 2**: Use the Code-OSS Editor in SageMaker Studio to deploy the model to an inference endpoint.
- **Module 3**: Still using the Code-OSS Editor, build an end-to-end pipeline to download the data source, perform feature engineering, train a model, register it in the model registry, and deploy it into an inference endpoint.
- **Module 4**: Build a HTTP API using Amazon API Gateway and an AWS Lambda function to invoke the Amazon SageMaker endpoint for inference.
- **Module 5**: Use a web client to invoke the HTTP API and perform inference.

Please follow the order of modules because the modules depend on the results from the previous modules.

## Running this workshop

### AWS-run event using AWS Workshop Studio
If you are attending the **Scale complete ML development with Amazon SageMaker Studio** workshop run by AWS, the AWS event facilitator has provided you access to a temporary AWS account preconfigured for this workshop. Proceed to <a href="./00_open_sagemaker_studio/README.md">**Module 0: Open SageMaker Studio**</a>.

### Self-paced using your AWS account
If you want to use your own AWS account, you'll have to execute some preliminary configuration steps as described in the **<a href="./setup/README.md">Setup Guide</a>**.

> :warning: **Running this workshop in your AWS account will incur costs**. You will need to delete the resources you create to avoid incurring further costs after you have completed the workshop. See the [clean up steps](./cleanup/README.md).

## Acknowledgements

Dua, D. and Graff, C. (2019). UCI Machine Learning Repository [http://archive.ics.uci.edu/ml]. Irvine, CA: University of California, School of Information and Computer Science.

## Authors

[Giuseppe A. Porcelli](https://it.linkedin.com/in/giuporcelli) - Principal ML Specialist Solutions Architect - Amazon Web Services<br />
[Antonio Duma](https://it.linkedin.com/in/antoniod82) - Senior Startup Solutions Architect - Amazon Web Services <br />
[Hasan Poonawala](https://www.linkedin.com/in/hasanp) - Senior ML Specialist Solutions Architect - Amazon Web Services <br />
[Mehran Nikoo](https://www.linkedin.com/in/mnikoo/) - Senior Solutions Architect - Amazon Web Services <br />
[Bruno Pistone](https://www.linkedin.com/in/bpistone) - AI/ML Specialist Solutions Architect - Amazon Web Services<br />
[Durga Sury](https://www.linkedin.com/in/durgasury) - ML Solutions Architect - Amazon Web Services<br />