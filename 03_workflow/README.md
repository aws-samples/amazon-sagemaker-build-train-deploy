# Module 3: Create a complete deployment pipeline

1. In the Explorer window, from folder **03_workflow**, open the Python file **pipeline.py**.

    <img src="../images/module_03/open_pipeline_script.png" alt="Open pipeline script" width="800px" />

2. Make yourself familiar with the code in **pipeline.py**.

3. Choose the **Run Python File** icon at the top right, as displayed below:

    <img src="../images/module_03/run_pipeline_script.png" alt="Open pipeline script" width="800px" />

4. The Terminal window will show the progress of the exectuion. The last operation in the pipeline script will start the pipeline, and pipeline execution will continue in the background.

5. In the Explorer window, from folder **03_workflow**, open the Python file **list_pipeline_executions.py**.

6. Choose the **Run Python File** icon at the top right, as displayed below:

    <img src="../images/module_03/run_list_pipeline_executions.png" alt="List pipeline executions" width="800px" />

7. The Terminal window will display the status of the last pipeline execution, including the status of the steps and their respective states. Wait until the pipeline status shows **Succeeded**.

8. Go back to SageMaker Studio and choose **Deployment >> Endpoints** from the menu on the left. Locate the endpoints whose name starts with `sagemaker-btd-endpoint-`. Find the last deployed endpoint (note the **Created on** field), and make note of the endpoint name. You will need the endpoint name in the next module.

	<img src="../images/module_02/view_endpoints.png" alt="List of endpoints" width="800px" />

## Proceed to Module 4
You have completed Module 3: Create a complete deployment pipeline. Please proceed to [Module 4: Build a HTTP API using Amazon API Gateway and AWS Lambda](../04_api_gateway_and_lambda/README.md).