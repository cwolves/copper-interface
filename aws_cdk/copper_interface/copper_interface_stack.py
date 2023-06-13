import os
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_lambda as _lambda,
    aws_ssm as ssm,
    aws_iam as iam,
    Duration,
    RemovalPolicy,
)

import json


class CopperInterfaceStack(Stack):
    def __init__(self, scope, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # intialize some environment variables for the lambda function
        forwarder_environment = {
            "copper_receiver_url": "https://zof5dm3d636vqsqssv65rhs5f40qhsde.lambda-url.us-west-2.on.aws/",
        }

        # splunk parameters in order to send logs to splunk
        params = {
            "splunk_host": "The host name of the splunk instance. e.g. https://prd-p-foxn4.splunkcloud.com",
            "splunk_hec_token": "The token used to send logs to splunk. e.g. 1234-5678-9012-3456",
            "copper_api_token": "The token from cwolves.com to give access to the Copper API",
        }

        for param, description in params.items():
            param_name = f"/copper/forwarder/{param}"
            ssm.StringParameter(
                self,
                param,
                parameter_name=param_name,
                description=description,
                # this needs to be replaced by the end user
                string_value="PLACEHOLDER_VALUE",
            )
            forwarder_environment[param] = param_name
        # build lambda that will forward logs to Copper API
        # this lambda function is triggered when a new file is added to the bucket
        log_forwarder = _lambda.Function(
            self,
            "copper-log-forwarder",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="send.lambda_handler",
            code=_lambda.Code.from_asset(
                "copper_interface/lambda/forwarder",
                bundling={
                    "image": _lambda.Runtime.PYTHON_3_9.bundling_image,
                    "command": [
                        "bash",
                        "-c",
                        "pip install -r requirements.txt -t /asset-output && cp -r * /asset-output",
                    ],
                },
            ),
            environment=forwarder_environment,
            function_name="copper-log-forwarder",
            memory_size=1024,
            timeout=Duration.minutes(15),
            # this role gives the lambda function permission to write to CloudWatch logs
            role=iam.Role(
                self,
                "copper-classify-role",
                assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
                managed_policies=[
                    iam.ManagedPolicy.from_aws_managed_policy_name(
                        "service-role/AWSLambdaBasicExecutionRole",
                    ),
                ],
            ),
        )

        # log destination
        # TODO: bucket name has to be globally unique which prevents us from using a static name...
        bucket_logs = s3.Bucket(
            self,
            "copper-logs-destination",
            # bucket_name=f"copper-logs-destination-{uuid.uuid4()}",
            removal_policy=RemovalPolicy.DESTROY,
        )

        # trigger the lambda function when a new file is added to the bucket
        bucket_logs.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(log_forwarder),
        )

        # give the lambda function permission to access the bucket
        bucket_logs.grant_read(log_forwarder)

        # give the lambda function permission to delete the file after it is processed
        bucket_logs.grant_delete(log_forwarder)

        # lambda policy to access parameter store
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        with open("lambda_ssm_policy.json", "r") as f:
            lambda_ssm_policy = json.load(f)

        # replace placeholder vars
        lambda_ssm_policy["Resource"] = (
            lambda_ssm_policy["Resource"]
            .replace("<account-id>", self.account)
            .replace("<region>", self.region)
        )
        # use iam to attach the policy to the lambda function
        log_forwarder.add_to_role_policy(
            iam.PolicyStatement.from_json(lambda_ssm_policy)
        )
