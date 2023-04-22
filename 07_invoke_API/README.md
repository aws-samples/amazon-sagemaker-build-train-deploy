# Invoke the API from a client

To perform inference from a client application, you will use a web tool called **ReqBin**, which allows to send HTTP requests to APIs.

- Access ReqBin at https://reqbin.com/
- Configure the client as shown in the following screenshot:

    <img src="images/reqbin.png" alt="Invoke from client" />

Make sure you:
- Provide the address of the Amazon API Gateway API you deployed in the previous step.
- Set the method to POST
- Set the content type to text/plain
- Add an inference record as content. Example: `L, 298.4, 308.2, 1582, 70.7, 216`

Then, click on **Send** to execute the request and get the inference result.

<h2>Well done!</h2>

By executing this step, you have completed the module and the main flow of the workshop.
<br/>
You can now move to <a href="../08_workflow/">**Module 08**</a> to start looking at the model build workflow.





