# https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-collector-api?tabs=python
import json
import requests
import datetime
import hashlib
import hmac
import base64


def send_logs_sentinel(json_data, customer_id, shared_key, log_type):
    body = json.dumps(json_data)

    #####################
    ######Functions######
    #####################

    # Build the API signature
    def build_signature(
        customer_id, shared_key, date, content_length, method, content_type, resource
    ):
        x_headers = "x-ms-date:" + date
        string_to_hash = (
            method
            + "\n"
            + str(content_length)
            + "\n"
            + content_type
            + "\n"
            + x_headers
            + "\n"
            + resource
        )
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
        ).decode()
        authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
        return authorization

    # Build and send a request to the POST API
    def post_data(customer_id, shared_key, body, log_type):
        method = "POST"
        content_type = "application/json"
        resource = "/api/logs"
        rfc1123date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        content_length = len(body)
        signature = build_signature(
            customer_id,
            shared_key,
            rfc1123date,
            content_length,
            method,
            content_type,
            resource,
        )
        uri = (
            "https://"
            + customer_id
            + ".ods.opinsights.azure.com"
            + resource
            + "?api-version=2016-04-01"
        )

        headers = {
            "content-type": content_type,
            "Authorization": signature,
            "Log-Type": log_type,
            "x-ms-date": rfc1123date,
        }

        response = requests.post(uri, data=body, headers=headers)
        if response.status_code >= 200 and response.status_code <= 299:
            print("Accepted")
            print(response.status_code)
        else:
            print("Response code: {}".format(response.status_code))
            print(response.text)

    post_data(customer_id, shared_key, body, log_type)


if __name__ == "__main__":
    # Update the customer ID to your Log Analytics workspace ID
    customer_id = "6bf5a2a8-3dc7-4810-bc58-db5dfbbbd45a"

    # For the shared key, use either the primary or the secondary Connected Sources client authentication key
    shared_key = "Z3yZSWCTzaenW3dB+RdBQOJQ/qHWiQzNPxiNqby3DmXcXhTyP25FkGSj6aI4J6f8IGIuzf0gCr0OZoIfDaPbaQ=="

    # The log type is the name of the event that is being submitted
    log_type = "WebMonitorTest"

    # An example JSON web monitor object
    json_data = [
        {
            "test-bool": True,
            "test-int": 1,
            "test-float": 1.1,
            "test-string": "test",
            "test-list": [1, 2, 3],
            "test-dict": {"a": 1, "b": 2},
        },
        {
            "test-bool": False,
            "test-int": 2,
            "test-float": 2.2,
            "test-string": "test2",
            "test-list": [4, 5, 6],
            "test-dict": {"c": 3, "d": 4},
        },
    ]
    send_logs_sentinel(json_data, customer_id, shared_key, log_type)
