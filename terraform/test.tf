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

# SSM parameters 1
resource "aws_ssm_parameter" "splunk_host" {
  name        = "/copper/forwarder/splunk_host"
  description = "The host name of the splunk instance. e.g. prd-p-foxn4"
  type        = "String"
  value       = "PLACEHOLDER_VALUE"
  overwrite = true
}

# SSM parameters 2
resource "aws_ssm_parameter" "splunk_hec_token" {
  name        = "/copper/forwarder/splunk_hec_token"
  description = "The token used to send logs to splunk. e.g. 1234-5678-9012-3456"
  type        = "SecureString"
  value       = "PLACEHOLDER_VALUE"
  overwrite = true
}

# SSM parameters 3
resource "aws_ssm_parameter" "copper_api_token" {
  name        = "/copper/forwarder/copper_api_token"
  description = "The token from cwolves.com to give access to the Copper API"
  type        = "SecureString"
  value       = "PLACEHOLDER_VALUE"
  overwrite = true
}

# Lambda can log events with this policy
resource "aws_iam_policy" "lambda_basic_execution" {
  name = "lambda-basic-execution"
  path = "/"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# Create lambda execution role that has the policy above
resource "aws_iam_role" "lambda_execution" {
  name = "lambda-execution"
  path = "/"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Create the Lambda function
resource "aws_lambda_function" "log_forwarder" {
  function_name = "copper-log-bucket-forwarder"
  handler       = "send.lambda_handler"
  filename      = "lambda_forwarder.zip"
  role          = aws_iam_role.lambda_execution.arn
  runtime       = "python3.9"
  memory_size   = 1024
  timeout       = 300 # 5 minutes

  # Set up the environment variables
  environment {
    variables = {
      copper_receiver_url = "https://zof5dm3d636vqsqssv65rhs5f40qhsde.lambda-url.us-west-2.on.aws/",
      splunk_host         = "/copper/forwarder/splunk_host",
      splunk_hec_token    = "/copper/forwarder/splunk_hec_token",
      copper_api_token    = "/copper/forwarder/copper_api_token",
    }
  }
}


# bucket to put logs
resource "aws_s3_bucket" "bucket_logs" {
  bucket = "copper-logs-destination"
}

resource "aws_s3_bucket_notification" "bucket_logs_notification" {
  bucket = aws_s3_bucket.bucket_logs.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.log_forwarder.arn
    events              = ["s3:ObjectCreated:*"]
  }
}

# policy to grant lambda permission to read from bucket

resource "aws_lambda_permission" "log_forwarder_s3_read_permission" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.log_forwarder.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.bucket_logs.arn
}

resource "aws_s3_bucket_policy" "bucket_logs_policy" {
  bucket = aws_s3_bucket.bucket_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowLambdaFunctionToReadObjects"
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
        ]
        Resource = "${aws_s3_bucket.bucket_logs.arn}/*"
      },
      {
        Sid    = "AllowLambdaFunctionToDeleteObjects"
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
        Action = [
          "s3:DeleteObject",
        ]
        Resource = "${aws_s3_bucket.bucket_logs.arn}/*"
      }
    ]
  })
}


# policy to grant lambda permission to read from SSM
resource "aws_iam_policy" "lambda_ssm_policy" {
  name_prefix = "lambda-ssm-policy-"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "AllowLambdaToAccessParameterStoreFolder"
        Effect   = "Allow"
        Action   = ["ssm:GetParametersByPath", "ssm:GetParameter"]
        Resource = "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/copper/forwarder/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_ssm_policy_attachment" {
  policy_arn = aws_iam_policy.lambda_ssm_policy.arn
  role       = aws_lambda_function.log_forwarder.role
}
