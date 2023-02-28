import requests
import boto3
import os


def lambda_handler(event, context):
    for record in event["Records"]:
        bucket_name = record["s3"]["bucket"]["name"]
        object_key = record["s3"]["object"]["key"]
        object_size = record["s3"]["object"]["size"]
    s3 = boto3.resource(
        service_name="s3",
    )
    bucket = s3.Bucket(bucket_name)
    # read in log data
    log_data = bucket.Object(object_key).get()["Body"].read().decode("utf-8")

    param_store = boto3.client("ssm")
    try:
        response = param_store.get_parameter(
            Name=os.environ["splunk_host"], WithDecryption=False
        )
        splunk_host = response["Parameter"]["Value"]

        response = param_store.get_parameter(
            Name=os.environ["splunk_hec_token"], WithDecryption=False
        )
        splunk_hec_token = response["Parameter"]["Value"]

        # send a request to the lambda function
        lambda_fn_url = os.environ["copper_receiver_url"]
        response = requests.post(
            lambda_fn_url,
            json={
                "splunk_host": splunk_host,
                "splunk_hec_token": splunk_hec_token,
                "log_data": log_data,
                "copper_api_token": "",
                "sentinel": "",
                "log_type",
            },
        )

        # delete the file from the bucket
        bucket.Object(object_key).delete()
        return response.json()

    except Exception as e:
        print(
            "This should not require any configuration. Something went wrong when deploying the stack."
        )
        raise e
