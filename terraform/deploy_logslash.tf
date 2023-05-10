# This file is a template to deploy a bucket, lambda, and permissions to forward logs to Copper.
# We've anticipated you will make bespoke changes according to your cloud environment, please contact thatcher@cwolves.com for support :)
provider "aws" {
  region = "us-west-2"
}

# source the current region from the aws provider
data "aws_region" "current" {}


# replace this with the name of the bucket you want to create
# if you have a bucket you want to use already:
# 1. replace with the name of your bucket
# 2. remove the aws_s3_bucket resource below
# 3. add your bucket id to the aws_s3_bucket_notification resource (at the bottom)
locals {
  bucket_name = "log-bucket-for-copper-2"
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
resource "aws_s3_bucket" "logs_bucket" {
  bucket = local.bucket_name
}

# role for lambda
resource "aws_iam_role" "lambda_execution" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# policy to read from bucket
resource "aws_iam_policy" "lambda_permissions" {
  name = "lambda_permissions_policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:s3:::${local.bucket_name}}",
          "arn:aws:s3:::${local.bucket_name}/*"
        ]
      },
      {
        Action = [
          "ssm:GetParameter"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:ssm:*:*:parameter/copper/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_execution_permissions" {
  policy_arn = aws_iam_policy.lambda_permissions.arn
  role       = aws_iam_role.lambda_execution.name
}

resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.log_forwarder.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.logs_bucket.arn
}

# This lambda function pulls downloads logs from a bucket and forwards them to the Copper API.
# It is triggered by Create Events on the bucket.
resource "aws_lambda_function" "log_forwarder" {
  function_name = "copper-log-bucket-forwarder-2"
  handler       = "send.lambda_handler"
  filename      = "lambda_forwarder.zip"
  role          = aws_iam_role.lambda_execution.arn
  runtime       = "python3.9"
  memory_size   = 512
  timeout       = 303 # 5 minutes

  environment {
    variables = {
      copper_receiver_url   = "https://zof5dm3d636vqsqssv65rhs5f40qhsde.lambda-url.us-west-2.on.aws/",
      splunk_host_path      = "/copper/forwarder/splunk_host",
      splunk_hec_token_path = "/copper/forwarder/splunk_hec_token",
      copper_api_token_path = "/copper/forwarder/copper_api_token",
    }
  }
}

# log group for lambda
resource "aws_cloudwatch_log_group" "lambda_logs_group" {
  name = "/aws/lambda/${aws_lambda_function.log_forwarder.function_name}"
}

# log stream
resource "aws_cloudwatch_log_stream" "lambda_logs_stream" {
  name           = "log_forwarder"
  log_group_name = aws_cloudwatch_log_group.lambda_logs_group.name
}

# permission for cloudwatch logs to invoke lambda
resource "aws_lambda_permission" "cloudwatch_logs_permission" {
  statement_id  = "AllowExecutionFromCloudWatchLogs"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.log_forwarder.arn
  principal     = "logs.${data.aws_region.current.name}.amazonaws.com"

  source_arn = aws_cloudwatch_log_group.lambda_logs_group.arn
}

# this notification triggers the lambda function when a file is created in the bucket
resource "aws_s3_bucket_notification" "logs_bucket_notification" {
  bucket = aws_s3_bucket.logs_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.log_forwarder.arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_bucket]
}

