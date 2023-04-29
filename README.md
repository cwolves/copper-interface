# Copper Interface

This repository contains infrastructure as code to quickly get started with the Copper API.

In short, to use our API:

1. Gather your JSON Log data (we're working on other formats)
2. Send it to our AWS Lambda based API ('https://zof5dm3d636vqsqssv65rhs5f40qhsde.lambda-url.us-west-2.on.aws/')

For any questions, feature requests, or suggestions reach out to thatcher@cwolves.com. I respond quickly!

## Copper API

The Copper API sits between your log producers and your SIEM. It doesn't matter where these producers exist as long as they can send their JSON log data to the Copper API over the internet.

NOTE: We are **actively** developing capability to accept XML data.

One way to use our API is to push all of your logs to a bucket and use a Lambda to forward them to the Copper API. Our API will return the slashed data to you and This repository is allows you to instantly set up the AWS resources via their CDK for this pattern.

Additionally, this repository contains an example Python script that shows how to send logs to the Copper API directly.

## API Specification

Endpoint: <https://zof5dm3d636vqsqssv65rhs5f40qhsde.lambda-url.us-west-2.on.aws/>

Method: POST

Request Body:

| Name                 | Type   | Required | Description                                                  |
| -------------------- | ------ | -------- | ------------------------------------------------------------ |
| json_log_str         | string | Yes      | A string representation of a JSON array of log data.         |
| api_token            | string | Yes      | An API token from <https://cwolves.com/dashboard/api-tokens/>. |
| splunk_hec_token     | string | No       | A token for Splunk HEC.                                      |
| splunk_host          | string | No       | The Splunk host. e.g.                                        |
| splunk_index         | string | No       | The desired index for Splunk HEC.                            |
| sentinel_customer_id | string | No       | The customer ID for Microsoft Sentinel.                      |
| sentinel_shared_key  | string | No       | The shared key for Microsoft Sentinel.                       |
| sentinel_log_type    | string | No       | The desired log type for Microsoft Sentinel.                 |

Response Body:

| Name     | Type   | Description                                         |
| -------- | ------ | --------------------------------------------------- |
| logs     | array  | The slashed log data.                               |
| sentinel | object | Metadata regarding data sent to Microsoft Sentinel. |
| splunk   | object | Metadata regarding data sent to Splunk.             |

Example Request:

```json
{
  "json_log_str": "[{\"log\": \"log1\"}, {\"log\": \"log2\"}]",
  "api_token": "cw",
  "splunk_hec_token": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "splunk_host": "prd-x-xxxxx",
  "splunk_index": "main",
  "sentinel_customer_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "sentinel_shared_key": "xxxxxxxxxxxxxxxxxxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx==",
  "sentinel_log_type": "WebMonitorTest"
}
```

## Quickest Start (Python Script)

Use the example Python script `direct_to_api/send_logs.py` to send logs to our API.

## Quick Start (Terraform)

We've just added this, please let us know if you have any issues.

### Prerequisites

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

## Quick Start (AWS CDK)

You can use our infrastructure as code with the AWS CDK to quickly create a stack in your AWS account. At the end you'll have a bucket which, when json files are dropped into it, will send logs to our API.

### Prerequisites

- npm, Node.js [Install](https://nodejs.org/en/download/)
- Python [Install](https://www.python.org/downloads/)
- AWS Account [Sign Up](https://aws.amazon.com/)
- AWS CLI Access [Instructions](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
- AWS CDK [Guide](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html)
- Splunk HEC Endpoint [Guide](https://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector)

0. Prerequisites  
   Install Libraries  
   `npm i -g aws-cdk`  
   `pip install -r requirements.txt`  
   [Sign Up](https://cwolves.com) for a Cwolves Account
1. Clone this repository onto your local machine.

   `git clone git@github.com:arctype-dev/copper-interface.git`

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
