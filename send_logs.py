import time
import requests
import json


def send_logs_to_cwolves(json_log_str, splunk_hec_token, splunk_host):
    log_data_dict = json.loads(json_log_str)
    # is a json array
    # send logs 25_000 at a time
    print("processing", len(log_data_dict), "logs")
    start_time = time.time()

    # we can only send 6291456 bytes at a time
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
    # round down to nearest 1000
    batch_size = batch_size // 1000 * 1000

    print("batch size", batch_size)
    print("bytes per line", bytes_per_line)
    print("log data size", log_data_size)

    if len(log_data_dict) > batch_size:
        for i in range(0, len(log_data_dict), batch_size):
            log_data = log_data_dict[i : i + batch_size]
            log_data = json.dumps(log_data)
            try:
                url = "https://copper.p.rapidapi.com/slash"
                headers = {
                    "X-RapidAPI-Key": "25bd864c53msha9976c156c6791ap1eb57djsn2eb7a61dedbc",
                    "X-RapidAPI-Host": "copper.p.rapidapi.com"
                }
                response = requests.post(
                    url,
                    json={
                        "splunk_host": splunk_host,
                        "splunk_hec_token": splunk_hec_token,
                        "log_data": log_data,
                        "copper_api_token": "",  # not used yet
                        "log_type": "json",  # not used yet
                    },
                    headers=headers,
                    # timeout=0.0000000001,
                )
                print(response.status_code, response.text)
            # hack to not wait for response
            except requests.exceptions.ConnectTimeout:
                pass
            # print(response.status_code, response.text)
            print(
                "percent done",
                (i / len(log_data_dict)) * 100,
                "%",
                "time taken",
                time.time() - start_time,
                "seconds",
                "minutes",
                (time.time() - start_time) / 60,
            )
    end_time = time.time()
    print(
        f"All done! Time taken: {end_time - start_time} seconds",
        "Minutes: ",
        (end_time - start_time) / 60,
    )


if __name__ == "__main__":
    with open("./log_data/example_logs.json") as f:
        log_data = f.read()

    splunk_hec_token = "4549d728-f40b-409d-8d48-6f6bc5d9edfd"  # TODO: change this
    splunk_host = "prd-p-y2slg"  # TODO: change this

    send_logs_to_cwolves(log_data, splunk_hec_token, splunk_host)
