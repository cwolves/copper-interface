# Copper Interface

This repository contains infrastructure as code, and examples to quickly get started with the Copper API.

In summary, to use our API:

1. Gather your JSON Log data, Windows Event Log data, or XML data.
2. Send it to our AWS Lambda based API ('https://zof5dm3d636vqsqssv65rhs5f40qhsde.lambda-url.us-west-2.on.aws/')

Below, you will find documentation on how to use our API. You can:

1. Use our API directly by sending a POST request to our API. ([API Specification](#api-specification)) ([Example Python Script](#quick-start-with-python))
2. Use the AWS CDK to quickly create a stack in your AWS account. This will create a bucket in AWS that will forward file data to our API. ([AWS CDK](#quick-start-using-aws-cdk))
3. Use Terraform to quickly create a stack in your AWS account. This will create a bucket in AWS that will forward file data to our API. ([Terraform](#quick-start-using-terraform))

For any questions, feature requests, or suggestions reach out to thatcher@cwolves.com. I respond quickly!

## Copper API

The Copper API sits between your log producers and your SIEM. It doesn't matter where these producers exist as long as they can send their JSON, XML, or Windows Event log data to the Copper API over the internet.

## API Specification

You can send logs to our API via a POST request. The request body should be a JSON object with the following fields:

Endpoint: <https://zof5dm3d636vqsqssv65rhs5f40qhsde.lambda-url.us-west-2.on.aws/>

Method: POST

Request Body:

| Name                 | Type   | Required | Description                                                                                                                                           |
| -------------------- | ------ | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| json_log_str         | array  | Yes      | A JSON array of strings. Each item can be either JSON or XML format. If you have Windows Event Logs, each event should be a string item in the array. |
| api_token            | string | Yes      | A Cwolves API token, visit <https://cwolves.com/dashboard/api-tokens/>.                                                                               |
| splunk_hec_token     | string | No       | A token for Splunk HEC.                                                                                                                               |
| splunk_host          | string | No       | The Splunk host. e.g.                                                                                                                                 |
| splunk_index         | string | No       | The desired index for Splunk HEC.                                                                                                                     |
| sentinel_customer_id | string | No       | The customer ID for Microsoft Sentinel.                                                                                                               |
| sentinel_shared_key  | string | No       | The shared key for Microsoft Sentinel.                                                                                                                |
| sentinel_log_type    | string | No       | The desired log type for Microsoft Sentinel.                                                                                                          |

Note: Splunk and Sentinel fields are optional. If you do not provide them, the API will not send data to Splunk or Sentinel. The slashed data will be returned in the response body. If you'd like to use splunk or sentinel, use all of the fields for that service.

Response Body:

| Name     | Type   | Description                                         |
| -------- | ------ | --------------------------------------------------- |
| logs     | array  | The slashed log data.                               |
| sentinel | object | Metadata regarding data sent to Microsoft Sentinel. |
| splunk   | object | Metadata regarding data sent to Splunk.             |

Example Requests:

```json
{
  "json_log_str": "[{\"log\": \"logdata1\"}, {\"log\": \"logdata2\"}]",
  "api_token": "cw"
}
```

```json
{
  "json_log_str": "[{\"log\": \"logdata1\"}, {\"log\": \"logdata2\"}]",
  "api_token": "cw",
  "splunk_hec_token": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "splunk_host": "prd-x-xxxxx",
  "splunk_index": "main"
}
```

```json
{
  "json_log_str": "[{\"log\": \"logdata1\"}, {\"log\": \"logdata2\"}]",
  "api_token": "cw",
  "sentinel_customer_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "sentinel_shared_key": "xxxxxxxxxxxxxxxxxxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx==",
  "sentinel_log_type": "WebMonitorTest"
}
```

Here is an example request with python:

```python
url = "https://zof5dm3d636vqsqssv65rhs5f40qhsde.lambda-url.us-west-2.on.aws/"
response = requests.post(
      url,
      json={
         "log_data": "[{\"log\": \"logdata1\"}, {\"log\": \"logdata2\"}]"
         "api_token": 'cw-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
         # optional, pass in desired index for Splunk HEC
         "splunk_host": 'prd-x-xxxxx',
         "splunk_hec_token": 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
         "splunk_index": 'main',
         # optional, pass in desired log type for MSFT Sentinel
         "sentinel_customer_id": 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
         "sentinel_shared_key": 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx==',
         "sentinel_log_type": 'WebMonitorTest'
      },
)
```

## Quick Start with Python

You can look at our example Python script `direct_to_api/send_logs.py`. It shows you how to batch JSON data into 6mb chunks and send it to our API. You will need an API token from <https://cwolves.com/dashboard/api-tokens/> to use this script.

## Quick Start using Terraform

We've just added this, please let us know if you have any issues.

### Prerequisites

You should be comfortable working with Terraform.

- Terraform [Install](https://learn.hashicorp.com/tutorials/terraform/install-cli)
- AWS Account [Sign Up](https://aws.amazon.com/)
- Splunk HEC Endpoint [Guide](https://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector)

0. Prerequisites
   [Sign Up](https://cwolves.com) for a Cwolves Account
1. Clone this repository onto your local machine.

   `git clone git@github.com:arctype-dev/copper-interface.git`

2. Change into the directory.

   `cd copper-interface/terraform`

3. Initialize Terraform. This creates a stack with the resources required to deploy a stack via Terraform. You can see the stack in CloudFormation.

   `terraform init`

4. Deploy the stack. This creates the resources in your AWS account. You can see the stack in CloudFormation.

   `terraform apply`

## Quick Start using AWS CDK

You can use our infrastructure as code with the AWS CDK to quickly create a Cloud Formation Stack in your AWS account. At the end you'll have some AWS [resources](#cdk-resources), most importantly a bucket. when json files are dropped into it, file data will be forwarded to our API.

Note: We have not updated the CDK to work with Sentinel yet.

### Prerequisites

You should be comfortable using the AWS CLI, CDK, and Python.

- npm, Node.js [Install](https://nodejs.org/en/download/)
- Python [Install](https://www.python.org/downloads/)
- AWS Account [Sign Up](https://aws.amazon.com/)
- AWS CLI Access [Instructions](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
- AWS CDK [Guide](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html)
- Splunk HEC Endpoint [Guide](https://docs.splunk.com/Documentation/Splunk/9.0.4/Data/UsetheHTTPEventCollector)

0. Clone this repository onto your local machine.

   `git clone git@github.com:arctype-dev/copper-interface.git`

1. Prerequisites
   Install Libraries  
   `npm i -g aws-cdk` (Command line tool to use the AWS CDK)  
   `pip install -r aws_cdk/requirements.txt`  
   [Sign Up](https://cwolves.com) for a Cwolves Account  
   Get an API Token from <https://cwolves.com/dashboard/api-tokens/>

2. Change into the directory.

   `cd copper-interface/aws_cdk`

3. Bootstrap the CDK. This creates a stack with the resources required to deploy a stack via the CDK. You can see the stack in CloudFormation.

   `cdk bootstrap`

4. Deploy the stack. This creates the resources in your AWS account. You can see the stack in CloudFormation.

   `cdk deploy`

5. Update the SSM parameters with your Splunk configuration.
   In your AWS console, go to Systems Manager > Parameter Store. You should see three parameters that were created by the stack. Update the values with your Splunk configuration and token from [Cwolves Dashboard](https://cwolves.com/dashboard).

   ![SSM Parameters](./readme_img/aws_parameter_store.png)

   Edit each parameter and update the values.

   ![SSM Parameter Values](./readme_img/set_splunk_param.png)

6. Now that everything is set up, drop files into the bucket `copperinterfacestack-copperlogsdestination`. The files should be in the json format. The files will be processed, reduced in size, and sent to the Splunk HEC endpoint you configured.

   ![Bucket](./readme_img/logs_bucket.png)

7. At anytime, if you'd like to completely the resources you created:

   `cdk destroy`

## CDK Resources

This stack creates resources that will enable you to drop logs into a bucket, and have the slashed version sent to Splunk.

### Log Bucket

The stack includes a single bucket to drop logs into. Simply upload a file with you logs in the json format. This bucket is NOT for long term storage, the files are deleted once they are processed by the forwarder lambda.

#### Lambda Event Notification

The bucket is configured to send an event notification to a lambda function when a file is dropped into the bucket. This will trigger the lambda to pull the file from the bucket and send it to Copper for processing along with your Splunk configuration parameters.

### Systems Manager Parameter Store

The stack initializes three parameters that you need to update with your own values. The first is `splunk_host` which is the hostname of your Splunk instance (e.g. 'prd-p-foxn4'). The second is `splunk_hec_token` which is the Authorization token for a Splunk HEC endpoint that you created. The third is `copper_api_token`

### Forwarder Lambda

The stack creates a lambda function that will be triggered by the bucket. The lambda function will take the file that was dropped into the bucket, and send the API token, splunk secrets, and data to the Copper API. Then, it will delete the file from the bucket.

#### Policies

The lambda function is given a policy to read from SSM Parameter Store within the folder `/copper/logslash/*`
