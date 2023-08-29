# Module 7: Invoke the API from a browser

To perform inference, you will use a web tool called **ReqBin** to send requests to new HTTP API. 

- Access ReqBin at https://reqbin.com/
- Configure the client as shown in the following screenshot:

    <img src="images/reqbin.png" alt="Invoke from client" />

Make sure you:
- Provide the address of the Amazon API Gateway API you deployed in the previous step.
- Set the method to POST
- Set the content type to text/plain
- Add an inference record as content. Example: `L, 298.4, 308.2, 1582, 70.7, 216`

Then, click on **Send** to execute the request and get the inference result.

## You have completed Module 7 

By finishing this module, you have completed the main flow of the workshop.

Open **08_workflow.ipynb** in module 8 to build a an Amazon SageMaker Pipeline for preprocessing and training jobs. 




