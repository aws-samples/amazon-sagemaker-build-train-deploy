# End to end Machine Learning with Amazon SageMaker

## Introduction

The Machine Learning process is an iterative process consisting of several steps:

- Identifying a business problem and the related machine learning problem
- Data ingestion, integration and preparation
- Data visualization and analysis, feature engineering, model training and model evaluation
- Model deployment, model monitoring and debugging

These steps are usually repeated multiple times to better meet business goals after the source data changes or performance of the model drops, for example.

The following diagram shows how the process works:

<img src="images/ml_process.png" alt="ML Process" />

After you deploy a model, you can integrate it with your own application to provide insights to the end users.

In this workshop, you will go through the steps required to build, train, and deploy a machine learning application on AWS using Amazon SageMaker. You will then deploy a HTTP API using Amazon API Gateway to receive inference requests from a web client and send it to an AWS Lambda function, which performs inference against the model. In the last module, you will automate the workflow using Amazon SageMaker Pipelines.

The final architecture is shown below:

<img src="images/architecture.png" alt="Architecture" />

## The Machine Learning task

You will use the <a href="https://archive.ics.uci.edu/ml/datasets/AI4I+2020+Predictive+Maintenance+Dataset">AI4I 2020 Predictive Maintenance Dataset</a> from the UCI Machine Learning Repository. This synthetic dataset reflects real predictive maintenance data encountered in industry.

The dataset consists of 10,000 records and 14 features, representing some measurements that have been collected on the machinery, plus the indication of failure, if any. This is a basic dataset that oversimplifies the Predictive Maintenance task. However, it keeps this workshop easy to follow while being a good representative of the various steps of the machine learning workflow.

Your goal is to build a simple machine learning model that predicts whether a piece of machinery is going to fail (<b>Predictive Maintenance</b>).

Following is an excerpt from the dataset:

|UDI|Product ID|Type|Air temperature [K]|Process temperature [K]|...|Machine failure|
|-------|-------|-------|-------|-------|-------|-------|
|1|M14860|M|298.1|308.6|...|0|
|2|L47181|L|298.2|308.7|...|0|
|3|L47182|L|298.1|308.5|...|0|
|51|L47230|L|298.9|309.1|...|1|

The target variable, **Machine failure**, is a binary attributes, so it suggests the problem is a binary classification problem.

## Modules

This workshops consists of eight modules:

- <a href="01_configure_sagemaker_studio/">**Module 01**</a>: Prepare Amazon SageMaker Studio and clone the GitHub repository.
- <a href="02_fast_experimentation/">**Module 02**</a>: Use Amazon SageMaker Studio Notebooks and standard Python libraries to perform fast experimentation.
- <a href="03_feature_engineering/">**Module 03**</a>: Perform data preprocessing and feature engineering using Amazon SageMaker Processing and SKLearn.
- <a href="04_train_model/">**Module 04**</a>: Train a binary classification model with the Amazon SageMaker open-source XGBoost container; the model will predict whether the machinery is going to fail. [Optional] Use Sagemaker Debugger to monitor training progress with rules and visualize training metrics like accuracy and feature importance.
- <a href="05_deploy_model/">**Module 05**</a>: Deploy the feature engineering and ML models as a pipeline using Amazon SageMaker hosting (inference pipelines). [Optional] Use Sagemaker Model Monitor to track data drift violations against the training data baseline.
- <a href="06_API_Gateway_and_Lambda/">**Module 06**</a>: Build a HTTP API using Amazon API Gateway and create an AWS Lambda function that invokes the Amazon SageMaker endpoint for inference.
- <a href="07_invoke_API/">**Module 07**</a>: Use a web client to invoke the HTTP API and get inferences.
- <a href="08_workflow/">**Module 08**</a>: Use Amazon SageMaker Pipelines to orchestrate the model build workflow and store models in model registry.

Please follow the order of modules because the modules depend on the results from the previous modules.

## Getting started

### AWS Event using Workshop Studio
The temporary AWS account provided configures the environment for you. Proceed to <a href="./01_configure_sagemaker_studio/README.md">**Module 01**</a>.

### Self-paced using your AWS account
If you want to use your own AWS account, you'll have to execute some preliminary configuration steps as described in the **<a href="./setup/README.md">Setup Guide</a>**.

> :warning: **Running this workshop in your AWS account will incur costs**. You will need to delete the resources you create to avoid incurring further costs after you have completed the workshop. Follow the [clean up steps](./cleanup/README.md).


## License

The contents of this workshop are licensed under the [Apache 2.0 License](./LICENSE).

## Acknowledgements

Dua, D. and Graff, C. (2019). UCI Machine Learning Repository [http://archive.ics.uci.edu/ml]. Irvine, CA: University of California, School of Information and Computer Science.

## Authors

[Giuseppe A. Porcelli](https://it.linkedin.com/in/giuporcelli) - Principal ML Specialist Solutions Architect - Amazon Web Services<br />
[Antonio Duma](https://it.linkedin.com/in/antoniod82) - Senior Startup Solutions Architect - Amazon Web Services <br />
[Hasan Poonawala](https://www.linkedin.com/in/hasanp) - Senior ML Specialist Solutions Architect - Amazon Web Services <br />
[Mehran Nikoo](https://www.linkedin.com/in/mnikoo/) - Senior Digital Native Solutions Architect - Amazon Web Services <br />
[Bruno Pistone](https://www.linkedin.com/in/bpistone) - AI/ML Specialist Solutions Architect - Amazon Web Services<br />
[Durga Sury](https://www.linkedin.com/in/durgasury) - ML Solution Architect - Amazon Web Services<br />