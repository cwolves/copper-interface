import json
import requests
import boto3
import os


def lambda_handler(event, context):
    for record in event["Records"]:
        bucket_name = record["s3"]["bucket"]["name"]
        object_key = record["s3"]["object"]["key"]
        object_size = record["s3"]["object"]["size"]
        file_extension = object_key.split(".")[-1]
    s3 = boto3.resource(
        service_name="s3",
    )
    bucket = s3.Bucket(bucket_name)
    # read in log data
    log_data = bucket.Object(object_key).get()["Body"].read().decode("utf-8")

    param_store = boto3.client("ssm")
    try:
        splunk_host = param_store.get_parameter(
            Name=os.environ["splunk_host"], WithDecryption=False
        )
        splunk_host = splunk_host["Parameter"]["Value"]

        splunk_hec_token = param_store.get_parameter(
            Name=os.environ["splunk_hec_token"], WithDecryption=False
        )
        splunk_hec_token = splunk_hec_token["Parameter"]["Value"]

        # TODO: safeguard when they forget to update parameter store value
        # write_error(bucket, "Please update the parameter store values for splunk_host and splunk_hec_token")

        # send a request to the lambda function
        lambda_fn_url = os.environ["copper_receiver_url"]
        # load log_data as a dict
        log_data_dict = json.loads(log_data)
        # is a json array
        # send logs 2500 at a time
        if len(log_data_dict) > 2500:
            for i in range(0, len(log_data_dict), 2500):
                log_data = log_data_dict[i : i + 2500]
                log_data = json.dumps(log_data)
                response = requests.post(
                    lambda_fn_url,
                    json={
                        "splunk_host": splunk_host,
                        "splunk_hec_token": splunk_hec_token,
                        "log_data": log_data,
                        "copper_api_token": "",
                        "log_type": f"{file_extension}",
                    },
                )

        # delete the file from the bucket
        bucket.Object(object_key).delete()

        print('All done!')

    except Exception as e:
        print(
            "This should only require Splunk parameter store configuration. Something went wrong when deploying the stack."
        )
        raise e

def write_error(bucket, error_txt):
    bucket.put_object(
        Key="ERROR.txt",
        Body=error_txt,
    )