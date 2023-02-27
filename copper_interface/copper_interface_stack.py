import os
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_lambda as _lambda,
    aws_ssm as ssm,
    aws_iam as iam,
)
import json


class CopperInterfaceStack(Stack):
    def __init__(self, scope, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # intialize some environmetn variables for the lambda function
        forwarder_environment = {
            "copper_receiver_url": "https://7ulq5dkwhuz7slwuf42p7cxxfe0pfghi.lambda-url.us-west-2.on.aws/",
        }

        # splunk parameters in order to send logs to splunk
        params = {
            "splunk_host": "The host name of the splunk instance. e.g. prd-p-foxn4",
            "splunk_hec_token": "The token used to send logs to splunk. e.g. 1234-5678-9012-3456",
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
            forwarder_environment[param.upper()] = param_name

        log_forwarder = _lambda.Function(
            self,
            "dependencies-layer",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="send.lambda_handler",
            code=_lambda.Code.from_asset("copper_interface/lambdas/forwarder"),
            environment=forwarder_environment,
            function_name="copper-log-forwarder",
        )

        # lambda layer version for the python requests library
        dependencies_layer = _lambda.LayerVersion(
            self,
            "forwarder-dependencies-layer",
            code=_lambda.Code.from_asset(
                "copper_interface/lambdas/dependencies",
                bundling={
                    "image": _lambda.Runtime.PYTHON_3_9.bundling_image,
                    "command": [
                        "bash",
                        "-c",
                        "pip install -r requirements.txt -t /asset-output && cp -r * /asset-output",
                    ],
                },
            ),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            layer_version_name="copper/forwarder-dependencies-layer",
        )

        # add the layer to the lambda function
        log_forwarder.add_layers(dependencies_layer)

        # holds logs
        bucket_logs = s3.Bucket(
            self,
            "copper-logs-bucket",
            bucket_name="copper-logs-bucket",
        )

        # trigger the lambda function when a new file is added to the bucket
        bucket_logs.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(log_forwarder),
        )

        # give the lambda function permission to access the bucket
        bucket_logs.grant_read(log_forwarder)

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
