import requests
import json


def send_logs(
    log_json_data,
    splunk_host,
    splunk_hec_token,
    splunk_source="logslash",
    splunk_index="main",
):
    """
    Takes json data and sends it to splunk.
    Args: log_json_data (dict?)
    """
    # splunk configuration
    port = 8088
    endpoint = "services/collector/event"
    if splunk_host == "localhost":
        host = "http://localhost"
    else:
        host = f"https://{splunk_host}.splunkcloud.com"

    url = f"{host}:{port}/{endpoint}?index={splunk_index}"
    # url = f"{host}:{port}/{endpoint}"
    print("sending to url", url)
    headers = {"Authorization": f"Splunk {splunk_hec_token}"}

    # not sure what causes this bug
    if isinstance(log_json_data, str):
        log_json_data = json.loads(log_json_data)

    # prepare logs for splunk, batches and converts to be splunk compatible
    json_data_str = map(
        lambda x: prepare_log_for_splunk(
            x,
            splunk_source=splunk_source,
        ),
        log_json_data,
    )
    json_data_batched = "".join(json_data_str)

    r = requests.post(
        url,
        headers=headers,
        data=json_data_batched,
        verify=False,
    )
    return r.status_code


def prepare_log_for_splunk(log_data, splunk_source="logslash"):
    """Moves the dict into the event key of a dict."""
    dumps = json.dumps(
        {
            "event": log_data,
            "source": f"{splunk_source}",
        },
        separators=(",", ":"),
    )
    return dumps


if __name__ == "__main__":
    # read in log_data/example_logs.json
    with open("./log_data/example_logs.json") as f:
        log_data = f.read()
    # send logs to splunk
    splunk_hec_token = "220f4d97-ccc7-4f2f-89a3-5e31f171b907"
    splunk_host = "prd-p-91czz"
    res = send_logs(
        log_data,
        splunk_host,
        splunk_hec_token,
        splunk_source="logslash",
        splunk_index="demo",
    )
    print(res)
