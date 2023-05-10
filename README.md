# Copper Interface

This repository contains infrastructure as code, and examples to quickly get started with the Copper API.

In summary, to use our API:

1. Gather your JSON Log data, Windows Event Log data, or XML data.
2. Send it to our AWS Lambda based API ('https://zof5dm3d636vqsqssv65rhs5f40qhsde.lambda-url.us-west-2.on.aws/')

Below, you will find documentation on how to use our API. There are 3 ways to get started:

1. Use our API directly by *sending* a POST request to our API. ([API Guide](./direct_to_api/README.md))
2. Use Terraform to quickly create a stack in your AWS account. This will create a bucket in AWS that will forward file data to our API. ([Terraform Guide](./terraform/README.md))
3. Use the AWS CDK to quickly create a stack in your AWS account. This will create a bucket in AWS that will forward file data to our API. ([AWS CDK Guide](./aws_cdk/README.md))

For any questions, feature requests, or suggestions reach out to thatcher@cwolves.com. I respond quickly!
