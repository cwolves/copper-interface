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
        print('got host', splunk_host, type(splunk_host))
        print(splunk_host['Parameter'].keys())
        print(splunk_host['Parameter']['Value'])
        splunk_host = splunk_host["Parameter"]["Value"]

        splunk_hec_token = param_store.get_parameter(
            Name=os.environ["splunk_hec_token"], WithDecryption=False
        )
        print('got token', splunk_hec_token, type(splunk_hec_token), splunk_hec_token['Parameter'].keys())
        print(splunk_hec_token['Parameter']['Value'])
        splunk_hec_token = splunk_hec_token["Parameter"]["Value"]

        # TODO: safeguard when they forget to update parameter store value
        # if (
        #     splunk_host["Parameter"]["Value"] == "PLACEHOLDER_VALUE"
        #     or splunk_hec_token["Parameter"]["Value"] == "PLACEHOLDER_VALUE"
        # ):
        #     error_txt = (
        #         "You must change the Splunk parameters before you can use our API."
        #     )
        #     print(error_txt)
        #     # write a txt file back to the bucket ERROR.txt
        #     bucket.put_object(
        #         Key="ERROR.txt",
        #         Body=error_txt,
        #     )
        #     return error_txt

        # send a request to the lambda function
        lambda_fn_url = os.environ["copper_receiver_url"]
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

        print(response.text)

    except Exception as e:
        print(
            "This should only require Splunk parameter store configuration. Something went wrong when deploying the stack."
        )
        raise e
