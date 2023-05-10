
# Quick Start using AWS CDK

You can use our infrastructure as code with the AWS CDK to quickly create a Cloud Formation Stack in your AWS account. At the end you'll have some AWS [resources](#cdk-resources), most importantly a bucket. when json files are dropped into it, file data will be forwarded to our API.

Note: We have not updated the CDK to work with Sentinel yet.

## Prerequisites

You should be comfortable using the AWS CLI, CDK, and Python.

- npm, Node.js [Install](https://nodejs.org/en/download/)
- Python [Install](https://www.python.org/downloads/)
- AWS Account [Sign Up](https://aws.amazon.com/)
- AWS CLI Access [Instructions](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
- AWS CDK [Guide](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html)
- Splunk HEC Endpoint [Guide](https://docs.splunk.com/Documentation/Splunk/9.0.4/Data/UsetheHTTPEventCollector)

0. Clone this repository onto your local machine.

   `git clone git@github.com:arctype-dev/copper-interface.git && cd copper-interface`

1. Prerequisites
   Install Libraries  
   `npm i -g aws-cdk` (Command line tool to use the AWS CDK)  
   `pip install -r aws_cdk/requirements.txt`  
   [Sign Up](https://cwolves.com) for a Cwolves Account  
   Get an API Token from <https://cwolves.com/dashboard/api-tokens/>

2. Change into the directory.

   `cd aws_cdk`

3. Bootstrap the CDK. This creates a stack with the resources required to deploy a stack via the CDK. You can see the stack in CloudFormation.

   `cdk bootstrap`

4. Deploy the stack. This creates the resources in your AWS account. You can see the stack in CloudFormation.

   `cdk deploy`

5. Update the SSM parameters with your Splunk configuration.
   In your AWS console, go to Systems Manager > Parameter Store. You should see three parameters that were created by the stack. Update the values with your Splunk configuration and token from [Cwolves Dashboard](https://cwolves.com/dashboard).

   ![SSM Parameters](./readme_img/aws_parameter_store.png)

   Edit each parameter and update the values.

   ![SSM Parameter Values](./readme_img/set_splunk_param.png)

6. Now that everything is set up, drop files into the bucket that was created. The files should be in the json format. The files will be processed, reduced in size, and sent to the Splunk HEC endpoint you configured.

   ![Bucket](./readme_img/logs_bucket.png)

7. At anytime, if you'd like to completely remove the resources you created:

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
