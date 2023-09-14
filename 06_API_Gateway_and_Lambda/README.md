# Module 6: Build a HTTP API using Amazon API Gateway and AWS Lambda

> ⚠️ This module does not have a Jupyter notebook. 

After deploying the model to a fully-managed Amazon SageMaker endpoint, you are ready to build a HTTP API that will be invoked by client applications to perform inferences.

Although you can call the Amazon SageMaker endpoint directly, adding an HTTP API in Amazon API Gateway in front of the SageMaker endpoint provides more control over user authorization, usage profiles, throttling, API versioning, etc. 

After building the HTTP API, the request flow would be as follows:

1. The client application send a HTTP POST request to the Amazon API Gateway endpoint.
2. The Amazon API Gateway application passes the request to an AWS Lambda function, which processes the request and calls the Amazon SageMaker HTTPS endpoint where the model is hosted.
3. Lambda function receives the inference response from Amazon SageMaker endpoint and send it back to the client via Amazon API Gateway.

Let's start building the HTTP API.

## Create the AWS Lambda function

1. Open **AWS Console** and go to the **Lambda** service.
2. In the **Functions** section, click on **Create function**.
3. Select **Author from scratch**.

<img src="images/lambda_1.png" alt="select blueprint" width="700px" />

4. Type **end-to-end-ml-lambda-function** in the function name textbox. Select _Use an existing role_ and then choose the IAM role whose name starts with **_LambdaInvokeSageMakerEndpointRole_** from the **Existing Role** dropdown. This will allow the function to invoke the real-time inference endpoint.

<img src="images/lambda_2.png" alt="Select IAM role" width="700px" />

5. You are now redirected to the Lambda function page. In the **Function code** section, double click "lambda_function.py":

<img src="images/lambda_5.png" alt="Configure API Gateway" width="700px" />

6. Replace the existing code with with the following snippet, making sure that the indentation is matching:

> ⚠️ **Warning**: the **ENDPOINT_NAME** variable must be set to the name of the endpoint that was deployed in the previus module of this workshop.

Note: You could also retrieve the endpoint name by viewing the endpoints in the SageMaker console:
<img src="images/lambda_7.png" alt="Endpoint list" width="700px" />
<img src="images/lambda_8.png" alt="Endpoint config" width="700px" />

```
# MIT No Attribution

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import boto3
import json
import csv
import os

# Remember to update the endpoint name with the name of the SageMaker endpoint
ENDPOINT_NAME = 'end-to-end-ml-sm-pipeline-endpoint-XXXXXXXXXX'
runtime= boto3.client('runtime.sagemaker')

def build_response(status_code, response_body):
    print(status_code)
    print(response_body)
    
    response = {
                'statusCode': status_code,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin' : '*',
                    'Access-Control-Allow-Credentials' : 'true',
		            'Access-Control-Allow-Headers': '*'
                },
            }

    if response_body is not None:
        response['body'] = str(response_body['predictions'][0]['score'])

    return response


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    
    if 'requestContext' in event:
        if event['httpMethod'] == 'OPTIONS':
            return build_response(200, '')

        elif event['httpMethod'] == 'POST':
            turbine_data = event['body']
            
            response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,
                                               ContentType='text/csv',
                                               Body=turbine_data)
            print(response)
            result = json.loads(response['Body'].read().decode())
            print(result)
            return build_response(200, result)
    
        else:
            return build_response(405, None)

```

The implementation is straightforward: the Lambda handler responds to OPTIONS and POST requests. When it receives a POST request, it invokes the Amazon SageMaker endpoint with the _Body_ parameter set to the request body, and when it receives the inference results, it sends the response to the caller.

7. Click **Deploy** to save changes.


## Create the Amazon API Gateway HTTP API

1. In **Function overview**, choose **Add trigger** and select **API Gateway** as the source.

<img src="images/lambda_3.png" alt="Configure API Gateway" width="700px" />

2. Choose **Create a new API** and keep the API Type as **HTTP API**. In the **Security** section, choose **Open**, then choose **Add**.

<img src="images/lambda_4.png" alt="Configure API Gateway" width="700px" />

3. Click on the **API Gateway** trigger and from the **Configuration** tab, make a note of _API endpoint_. You will need this in the next module.

<img src="images/lambda_6.png" alt="Configure API Gateway" width="700px" />

> The API expects a POST HTTP request that contains a comma-delimited list of feature values in the body. If you try to naviagate to the API endpoint URL in the browser, the API will receive a GET request, so it will return HTTP status code 405 (Method Not Allowed).

## You have completed module 6

You have now created an HTTP API that accepts inference requests. 

Proceed to module 7 to test the new HTTP API endpoint.