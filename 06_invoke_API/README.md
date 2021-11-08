# Invoke the API from a client

For the purpose of executing inferences from a client application we have are going to use a web tool called **ReqBin**, which allows to test APIs.

- Access ReqBin at https://reqbin.com/
- Configure the client as shown in the following screenshot:

    <img src="images/reqbin.png" alt="Invoke from client" />

You need to make sure to input the address of the Amazon API Gateway API deployed in the previous step, set the method to POST, content type to text/plain and add an inference record as content.

Then, click on **Send** to execute the request and get the inference result.

<h2>Well done!</h2>

By executing this step you have completed the module and the main flow of the workshop.
<br/>
You can now move to <a href="../07_workflow/">**Module 07**</a> to start looking at the model build workflow.





