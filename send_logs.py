import time
import requests
import json


def send_logs_to_cwolves(
    json_log_str, splunk_hec_token, splunk_host, splunk_index="main"
):
    log_data_dict = json.loads(json_log_str)
    # is a json array
    # send logs 25_000 at a time
    print("processing", len(log_data_dict), "logs")
    start_time = time.time()

    # we can only send 6291456 bytes at a time due to an aws lambda limitation
    # we need to find a batch size roughly equivalent to 6291456 bytes
    # 6291456 bytes = 6.29 MB

    # find the byte size of the log data
    log_data_size = len(json_log_str.encode("utf-8"))
    batch_size = log_data_size // 6091456

    # average the first 100 lines if available to figure out bytes per line
    if len(log_data_dict) > 100:
        log_data_dict_sample = log_data_dict[:100]
    else:
        log_data_dict_sample = log_data_dict
    bytes_per_line = 0
    for log in log_data_dict_sample:
        bytes_per_line += len(json.dumps(log).encode("utf-8"))
    bytes_per_line = bytes_per_line // len(log_data_dict_sample)
    batch_size = 5000000 // bytes_per_line
    # round down to nearest 1000 log lines
    batch_size = batch_size // 1000 * 1000

    print("batch size", batch_size)
    print("bytes per line", bytes_per_line)
    print("log data size", log_data_size)

    if len(log_data_dict) > batch_size:
        responses = []
        for i in range(0, len(log_data_dict), batch_size):
            log_data = log_data_dict[i : i + batch_size]
            log_data = json.dumps(log_data)
            try:
                url = "https://zof5dm3d636vqsqssv65rhs5f40qhsde.lambda-url.us-west-2.on.aws/"
                response = requests.post(
                    url,
                    json={
                        "splunk_host": splunk_host,
                        "splunk_hec_token": splunk_hec_token,
                        "log_data": log_data,
                        "api_token": "cw_GLAS2qMNhtRSGQDfeHw4695NO63f7VDq",
                        "log_type": "json",  # not used yet
                        "splunk_index": splunk_index,
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
    with open("./log_data/example_logs.json") as f:
        log_data = f.read()

    # PASS IN YOUR OWN SPLUNK PARAMETERS
    splunk_hec_token = "220f4d97-ccc7-4f2f-89a3-5e31f171b907"
    splunk_host = "prd-p-91czz"  # TODO: change this

    responses = send_logs_to_cwolves(
        log_data, splunk_hec_token, splunk_host, splunk_index="copper-demo"
    )

    # aggregate all of the json responses and save as a json file
    responses_json = ""
    for response in responses:
        responses_json += response.text
    with open("./log_data/responses.json", "w") as f:
        f.write(responses_json)
