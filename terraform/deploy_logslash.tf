# PROVIDE AWS_REGION
data "aws_region" "current" {}

# PROVIDE AWS_ACCOUNT_ID
data "aws_caller_identity" "current" {}

provider "aws" {
  region = "us-west-2" # Replace with your desired region
}

# The copper_receiver_url is essentially the url of the API
locals {
  forwarder_environment = {
    copper_receiver_url = "https://zof5dm3d636vqsqssv65rhs5f40qhsde.lambda-url.us-west-2.on.aws/"
  }
}

# SSM parameter descriptions
locals {
  splunk_host      = "The host name of the splunk instance. e.g. prd-p-foxn4"
  splunk_hec_token = "The token used to send logs to splunk. e.g. 1234-5678-9012-3456"
  copper_api_token = "The token from cwolves.com to give access to the Copper API"
}

# SSM parameters 1/3
resource "aws_ssm_parameter" "splunk_host" {
  name        = "/copper/forwarder/splunk_host"
  description = "The host name of the splunk instance. e.g. prd-p-foxn4"
  type        = "String"
  value       = "PLACEHOLDER_VALUE"
  overwrite   = true
}

# SSM parameters 2/3
resource "aws_ssm_parameter" "splunk_hec_token" {
  name        = "/copper/forwarder/splunk_hec_token"
  description = "The token used to send logs to splunk. e.g. 1234-5678-9012-3456"
  type        = "SecureString"
  value       = "PLACEHOLDER_VALUE"
  overwrite   = true
}

# SSM parameters 3/3
resource "aws_ssm_parameter" "copper_api_token" {
  name        = "/copper/forwarder/copper_api_token"
  description = "The token from cwolves.com to give access to the Copper API"
  type        = "SecureString"
  value       = "PLACEHOLDER_VALUE"
  overwrite   = true
}

# bucket to put logs
# TODO: change name or remove if you are bringing your own bucket
resource "aws_s3_bucket" "logs_bucket" {
  bucket = "FILL_BUCKET_NAME"
}

# This lambda function pulls downloads logs from a bucket and forwards them to the Copper API.
# It is triggered by Create Events on the bucket.
resource "aws_lambda_function" "log_forwarder" {
  function_name = "copper-log-bucket-forwarder-2"
  handler       = "send.lambda_handler"
  filename      = "lambda_forwarder.zip"
  role          = aws_iam_role.lambda_execution.arn
  runtime       = "python3.9"
  memory_size   = 1024
  timeout       = 300 # 5 minutes

  # Set up the environment variables
  # TODO: replace the bucket name if you are bringing your own bucket
  environment {
    variables = {
      copper_receiver_url   = "https://zof5dm3d636vqsqssv65rhs5f40qhsde.lambda-url.us-west-2.on.aws/",
      splunk_host_path      = "/copper/forwarder/splunk_host",
      splunk_hec_token_path = "/copper/forwarder/splunk_hec_token",
      copper_api_token_path = "/copper/forwarder/copper_api_token",
    }
  }
}




# this notfiication triggers the lambda function when a file is created in the bucket
resource "aws_s3_bucket_notification" "bucket_logs_notification" {
  bucket = aws_s3_bucket.bucket_logs.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.log_forwarder.arn
    events              = ["s3:ObjectCreated:*"]
  }
}

