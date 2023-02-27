# Copper Interface

This repo is intended to be cloned and pushed into CodeCommit within your own AWS account. Once it is in CodeCommit, you can create a CodePipeline from the provided yaml file. This pipeline creates a cdk stack which deploys a few resources that can get you started with the Copper API.

## Getting Started

### Prerequisites

- AWS Account
- AWS CLI Access
- Splunk [HEC](https://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector) Endpoint

### Installing

TODO: make better

1. Clone this repo onto your local machine
TODO: clone with repo url command
2. Set a remote branch to your own CodeCommit repo
3. Create a CodePipeline from the provided yaml file
4. Run the pipeline
5. Update the SSM parameters with your Splunk configuration
6. Drop files into the bucket

## Resources

This stack creates resources that will enable you to drop logs into a bucket, and have the reduced version sent to Splunk.

### Log Bucket

The stack includes a single bucket to drop logs into. Simply upload a file with you logs in the json, csv, or clf format. This bucket is NOT for long term storage, the files are deleted once they are processed by the forwarder lambda.

#### Lambda Event Notification

The bucket is configured to send an event notification to a lambda function when a file is dropped into the bucket. This will trigger the lambda to pull the file from the bucket and send it to Copper for processing along with your Splunk configuration parameters.

### Splunk Data in Systems Manager Parameter Store

The stack initializes two parameters that you need to update with your own values. The first is `splunk_host` which is the hostname of your Splunk instance (e.g. 'prd-p-foxn4'). The second is `splunk_hec_token` which is the Authorization token for a Splunk HEC endpoint that you created.

### Forwarder Lambda

The stack creates a lambda function that will be triggered by the bucket. The lambda function will take the file that was dropped into the bucket, and send it to Splunk. Then, it will delete the file from the bucket.

#### Policies

The lambda function is given a policy to read from SSM Parameter Store within the folder `/copper/logslash/*`