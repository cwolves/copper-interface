# This script demonstrates how to send logs to Copper's API
# At the bottom of the script, if __name__ == "__main__" you can pass in variables to send logs to Splunk HEC or MSFT Sentinel
# if you don't want to send logs to Splunk HEC or MSFT Sentinel, you can leave those variables as None, but you must pass an api token
#
# If you want to try out the API:
# 1. get an API token from https://cwolves.com/dashboard/api-tokens/
# if you want to try before you buy, contact us for a free token: thatchers@cwolves.com
# 2. Replace the api_token variable below with your API token
# 3. Run python send_logs.py within this directory
# This will send the example_logs.json file to Copper's API
# It will write the response to direct_to_api/log_data/responses.json
#
# You can use your own log data by replacing the example_logs.json file with your own data




import time
import requests
import json


def send_logs_to_cwolves(
    json_log_str,
    api_token,
    splunk_hec_token=None,
    splunk_host=None,
    splunk_index=None,
    sentinel_customer_id=None,
    sentinel_shared_key=None,
    sentinel_log_type=None,
):
    log_data_dict = json.loads(json_log_str)
    # is a json array
    print("processing", len(log_data_dict), "logs")
    start_time = time.time()
    ### BATCHING
    # This section demonstrates how to batch log data to meet a maximum byte size
    # that can be handled by the API.
    # we can only send 6291456 bytes at a time due to an aws lambda limitation
    # we need to find a batch size roughly equivalent to 6291456 bytes
    # 6291456 bytes = 6.29 MB

    # find the total byte size of the log data
    log_data_size = len(json_log_str.encode("utf-8"))

    # Due to the nature of logs, we need to find out how many lines this equates to
    # So that we don't send partial log lines

    # average the first 100 lines if available to figure out about how many bytes per line
    if len(log_data_dict) > 100:
        # TODO: make this sampling random
        log_data_dict_sample = log_data_dict[:100]
    else:
        log_data_dict_sample = log_data_dict

    bytes_per_line = 0
    for log in log_data_dict_sample:
        bytes_per_line += len(json.dumps(log).encode("utf-8"))
    bytes_per_line = bytes_per_line // len(log_data_dict_sample)

    # the batch size is the number of batches required
    # to send the log data in batches of about 5MB
    # 35MB of data will be sent in 7 batches
    batch_size = 5000000 // bytes_per_line

    # round down to nearest 1000 log lines
    batch_size = batch_size // 1000 * 1000

    print("batch size", batch_size)
    print("bytes per line", bytes_per_line)
    print("log data size", log_data_size)

    ### SENDING LOGS
    # Pass in the splunk host, splunk hec token, Copper api token, and log data
    # as a json array of log lines
    #
    responses = []
    # iterate through the log data in batches of 1000 log lines
    for i in range(0, len(log_data_dict), batch_size):
        log_data = log_data_dict[i : i + batch_size]
        # json array of log lines
        log_data = json.dumps(log_data)
        try:
            url = (
                "https://zof5dm3d636vqsqssv65rhs5f40qhsde.lambda-url.us-west-2.on.aws/"
            )
            response = requests.post(
                url,
                json={
                    "log_data": log_data,
                    "api_token": api_token,
                    # optional, pass in desired index for Splunk HEC
                    "splunk_host": splunk_host,
                    "splunk_hec_token": splunk_hec_token,
                    "splunk_index": splunk_index,
                    # optional, pass in desired log type for MSFT Sentinel
                    "sentinel_customer_id": sentinel_customer_id,
                    "sentinel_shared_key": sentinel_shared_key,
                    "sentinel_log_type": sentinel_log_type,
                },
                # hack to not wait for response
                # timeout=0.0000000001,
            )
            responses.append(response)
            print(
                "percent done",
                (i / len(log_data_dict)) * 100,
                "%",
                "time taken",
                time.time() - start_time,
                "seconds",
            )
            print(response.status_code)
        except requests.exceptions.ConnectTimeout:
            # hack to not wait for response
            pass

    end_time = time.time()
    print(f"All done! Time taken: {end_time - start_time} seconds")
    return responses


if __name__ == "__main__":
    # read in json log file
    with open("./log_data/example_logs.json") as f:
        # string of json data to be passed to function
        log_data = f.read()

    # OPTIONAL (SPLUNK): pass parameters to forward to splunk HEC
    # splunk_hec_token = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    # splunk_host = "prd-x-xxxxx"
    # splunk_index = "main"
    # OPTIONAL (SENTINEL): pass parameters to forward to MSFT sentinel
    # sentinel_customer_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    # sentinel_shared_key = "xxxxxxxxxxxxxxxxxxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=="
    # sentinel_log_type = "WebMonitorTest"

    # GET AN API TOKEN FROM https://cwolves.com/dashboard/api-tokens/
    api_token = "cw_xxxxxxxxxxxxxxxxxxxxxxxxxxx"

    responses = send_logs_to_cwolves(
        log_data,  # required
        api_token,  # optional
        # splunk_hec_token=splunk_hec_token, # optional
        # splunk_host=splunk_host, # optional
        # splunk_index=splunk_index, # optional
        # sentinel_customer_id=sentinel_customer_id, # optional
        # sentinel_shared_key=sentinel_shared_key, # optional
        # sentinel_log_type=sentinel_log_type, # optional
    )

    # aggregate all of the json responses and save as a json file
    responses_json = ""
    for response in responses:
        responses_json += response.text
    with open("./log_data/responses.json", "w") as f:
        f.write(responses_json)
