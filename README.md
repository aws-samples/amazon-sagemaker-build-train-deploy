# End-to-End ML Development with SageMaker Studio's New Experience and MLflow

In this workshop, you will go through the steps required to build a machine learning application on AWS using Amazon SageMaker Studio Experience. 

[//]: # (You will learn how to start experimentation in the SageMaker Studio environment using a familiar JupyterLab notebook experience and run your local code as a SageMaker Training job using the remote function feature. You will also learn how to use SageMaker Studio's Code Editor, which is based on Visual Studio Code – Open Source &#40;Code-OSS&#41;, to deploy the model into an endpoint and build a complete pipeline. You wull also learn how to build an HTTP endpoint using AWS Lambda and Amazon API Gateway to serve inference requests from a web client.)

### Modules and learning objectives

* **01 - Build and train models:** Perform data preparation and analysis using the SageMaker Studio Jupyterlab notebook experience and run your local code as a SageMaker Training job using the remote function feature. MLflow will be used to track and observe the experiments.
* **02 - Deploy models:** You will learn to use SageMaker Studio's Code Editor, which is based on Visual Studio Code – Open Source (Code-OSS), to deploy the model into an endpoint using [SageMaker ModelBuilder](https://docs.aws.amazon.com/sagemaker/latest/dg/how-it-works-modelbuilder-creation.html).
* **03 - Complete a complete pipeline:** You will create a complete pipeline from a workflow consisting of multiple steps using SageMaker Studio's Code Editor.
* **04 - Build HTTP API:** You will learn how to build an HTTP endpoint using AWS Lambda and Amazon API Gateway to serve inference requests from a web client.
* **05 - Invoke HTTP API:** You will invoke the HTTP API from the browser.

### SageMaker Features

This workshop covers multiple of the new features announced at AWS re\:Invent 2023. To learn more about these new features, watch the recording for the breakout session Scale complete ML development with Amazon SageMaker Studio (AIM325):
  * Remote and Step decorators for simple packaging and remote function calling.
  * ModelBuilder for easier packaging, local testing and deployment of models.
  * New SageMaker Studio Experience for Jupyterlab and Code Editor (based on Visual Studio Code - Code OSS).

Update October 15, 2024: The workshop has been extended to cover the following features

* MLflow for Experiments: Allows to utilize open source MLflow for observability through out your iterations.
* SageMaker Local Mode: Allows you to run created pipelines also locally using Docker, which makes your development life cycle much faster.
* Added Support for multi project isolation, by adding a custom project prefix for all resource like S3 buckets, training job names, inference endpoint names, pipeline names.   

<a href="https://www.youtube.com/embed/stB-F6jswno?si=20oR_uX5CFLo9ebR">
    <p align="center">
        <img src="https://img.youtube.com/vi/stB-F6jswno/0.jpg" />
        <br>
        AWS re:Invent 2023 - Scale complete ML development with Amazon SageMaker Studio (AIM325)
    </p>
</a>

## The machine learning process

The machine mearning process is an iterative process consisting of several steps:

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

## The machine learning task

You will use the [AI4I 2020 Predictive Maintenance Dataset](https://archive.ics.uci.edu/ml/datasets/AI4I+2020+Predictive+Maintenance+Dataset) from the UCI Machine Learning Repository. This synthetic dataset, which contains predictive maintenance data encountered in industry, consists of 10,000 records and 14 features. The features include various measurements collected from machinery and indication of whether the mechine is likely to fail. This basic dataset oversimplifies a predictive maintenance task. However, it keeps this workshop easy to follow while being a good representative of the various steps of the machine learning workflow. You can adapt the steps in this workshop to solve other machine learning tasks, including generative AI fine-tuning and deployment.

In this workshop, your goal is to build a simple machine learning model that predicts whether a piece of machinery is going to fail.

Following is an excerpt from the dataset:

|UDI|Product ID|Type|Air temperature [K]|Process temperature [K]|...|Machine failure|
|-------|-------|-------|-------|-------|-------|-------|
|1|M14860|M|298.1|308.6|...|0|
|2|L47181|L|298.2|308.7|...|0|
|3|L47182|L|298.1|308.5|...|0|
|51|L47230|L|298.9|309.1|...|1|

The binary (0 or 1) nature of the target variable, **Machine failure**, suggests you are solving a binary classification problem. In this workshop, you will build a logistic regression model, which will predict a continuous value in the range [0,1]. Using a regression model to solve a binary classification problem is a common approach. The predicted  score indicates the system’s certainty that the given observation belongs to the positive class. To make the decision about whether the observation should be classified as positive or negative, as a consumer of this score, you can interpret the score by picking a classification threshold (cut-off) and compare the score against it. Any observations with scores higher than the threshold are then predicted as the positive class and scores lower than the threshold are predicted as the negative class. To learn more about this approach, read https://docs.aws.amazon.com/machine-learning/latest/dg/binary-classification.html.

## Solution Architecture

This diagram shows what you will be building in this workshop:
<img src="images/architecture.png" alt="Architecture" />

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
[Mehran Nikoo](https://www.linkedin.com/in/mnikoo/) - ML & Generative AI Go-To-Market Specialist - Amazon Web Services <br />
[Bruno Pistone](https://www.linkedin.com/in/bpistone) - AI/ML Specialist Solutions Architect - Amazon Web Services<br />
[Durga Sury](https://www.linkedin.com/in/durgasury) - ML Solutions Architect - Amazon Web Services<br />
[Arlind Nocaj](https://www.linkedin.com/in/ArlindNocaj) - Senior Solutions Architect - Amazon Web Services<br />