import json
import requests
import boto3
import os
import xml.etree.ElementTree as ET


def lambda_handler(event, context):
    param_store = boto3.client("ssm")

    splunk_host = param_store.get_parameter(
        Name=os.environ["splunk_host_path"], WithDecryption=False
    )
    splunk_host = splunk_host["Parameter"]["Value"]

    splunk_hec_token = param_store.get_parameter(
        Name=os.environ["splunk_hec_token_path"], WithDecryption=False
    )
    splunk_hec_token = splunk_hec_token["Parameter"]["Value"]

    copper_api_token = param_store.get_parameter(
        Name=os.environ["copper_api_token_path"], WithDecryption=False
    )
    copper_api_token = copper_api_token["Parameter"]["Value"]

    for record in event["Records"]:
        bucket_name = record["s3"]["bucket"]["name"]
        object_key = record["s3"]["object"]["key"]

    s3 = boto3.resource(
        service_name="s3",
    )
    bucket = s3.Bucket(bucket_name)

    # read in log data
    log_data = bucket.Object(object_key).get()["Body"].read().decode("utf-8")

    if is_xml_format(log_data):
        log_type = "xml"
    elif is_json_format(log_data):
        log_type = "json"
    else:
        log_type = "text"
        raise Exception("Log data is not in JSON or XML format")

    log_data_batched = batch_logs(log_data, log_type)

    # send a request to the lambda function
    responses = []
    for log_data in log_data_batched:
        response = requests.post(
            os.environ["copper_receiver_url"],
            json={
                "splunk_host": splunk_host,
                "splunk_hec_token": splunk_hec_token,
                "log_data": log_data,
                "api_token": copper_api_token,
                "log_type": log_type,
            },
        )

        responses.append(response.text)

    return {"statusCode": 200, "body": json.dumps(responses)}


def is_json_format(json_string, encoding="utf-8"):
    try:
        json.loads(json_string, encoding=encoding)
        return True
    except:
        return False


def is_xml_format(xml_string):
    try:
        ET.fromstring(xml_string)
        return True
    except:
        return False


def batch_logs(log_data, log_type):
    log_data_size = len(log_data.encode("utf-8"))
    if log_type == "json":
        # load log_data as a dict
        log_data_array = json.loads(log_data)
    elif log_type == "xml":
        # we assume that XML data has top tag <Events> and each log is a child tag <Event>
        xml_data = log_data.strip()
        root = ET.fromstring("<Events>{}</Events>".format(xml_data))

        # array of xml strings
        log_data_array = [
            ET.tostring(event, encoding="unicode") for event in root.findall(".//Event")
        ]
    if log_data_size > 5000000:
        # average the first 100 lines if available to figure out bytes per line
        if len(log_data_array) > 100:
            log_data_dict_sample = log_data_array[:100]
        else:
            log_data_dict_sample = log_data_array
        bytes_ = 0
        for log in log_data_dict_sample:
            bytes_ += len(json.dumps(log).encode("utf-8"))
        bytes_per_line = bytes_ // len(log_data_dict_sample)
        # how many logs can we send in a single request?
        # 5MB is the max payload size for a lambda function
        batch_size = (5000000 // bytes_per_line) // 1000 * 1000
        # return an array of arrays where each array is a batch of logs in json str format
        return [
            log_data_array[i : i + batch_size]
            for i in range(0, len(log_data_array), batch_size)
        ]
    else:
        return [log_data_array]
