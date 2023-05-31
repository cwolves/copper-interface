# Copper API

The Copper API sits between your log producers and your SIEM. It doesn't matter where these producers exist as long as they can send their JSON, XML, or Windows Event log data to the Copper API over the internet.

## API Specification

You can send logs to our API via a POST request. The request body should be a JSON object with the following fields:

Endpoint: <https://zof5dm3d636vqsqssv65rhs5f40qhsde.lambda-url.us-west-2.on.aws/>

Method: POST

Request Body:

| Name                 | Type   | Required | Description                                                                                                                                           |
| -------------------- | ------ | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| log_data         | array  | Yes      | A JSON array of strings. Each item can be either JSON or XML format. If you have Windows Event Logs, each event should be a string item in the array. |
| api_token            | string | Yes      | A Cwolves API token, visit <https://cwolves.com/dashboard/api-tokens/>.                                                                               |
| splunk_hec_token     | string | No       | A token for Splunk HEC.                                                                                                                               |
| splunk_host          | string | No       | The Splunk host. e.g.                                                                                                                                 |
| splunk_index         | string | No       | The desired index for Splunk HEC.                                                                                                                     |
| sentinel_customer_id | string | No       | The customer ID for Microsoft Sentinel.                                                                                                               |
| sentinel_shared_key  | string | No       | The shared key for Microsoft Sentinel.                                                                                                                |
| sentinel_log_type    | string | No       | The desired log type for Microsoft Sentinel.                                                                                                          |

Note: The slashed data will always be returned in the response body. Splunk and Sentinel fields are optional. If you do not provide them, the API will not send data to Splunk or Sentinel. If you'd like to use splunk or sentinel, use all of the fields for that service.

Response Body:

| Name     | Type   | Description                                         |
| -------- | ------ | --------------------------------------------------- |
| logs     | array  | The slashed log data.                               |
| sentinel | object | Metadata regarding data sent to Microsoft Sentinel. |
| splunk   | object | Metadata regarding data sent to Splunk.             |

Example Requests:

```json
{
  "log_data": "[{\"log\": \"logdata1\"}, {\"log\": \"logdata2\"}]",
  "api_token": "cw-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

```json
{
  "log_data": "[{\"log\": \"logdata1\"}, {\"log\": \"logdata2\"}]",
  "api_token": "cw-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "splunk_hec_token": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "splunk_host": "prd-x-xxxxx",
  "splunk_index": "main"
}
```

```json
{
  "log_data": "[{\"log\": \"logdata1\"}, {\"log\": \"logdata2\"}]",
  "api_token": "cw-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "sentinel_customer_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "sentinel_shared_key": "xxxxxxxxxxxxxxxxxxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx==",
  "sentinel_log_type": "WebMonitorTest"
}
```

Here is an example request with python:

```python
url = "https://zof5dm3d636vqsqssv65rhs5f40qhsde.lambda-url.us-west-2.on.aws/"
response = requests.post(
      url,
      json={
         "log_data": "[{\"log\": \"logdata1\"}, {\"log\": \"logdata2\"}]"
         "api_token": 'cw-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
         # optional, pass in desired index for Splunk HEC
         "splunk_host": 'prd-x-xxxxx',
         "splunk_hec_token": 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
         "splunk_index": 'main',
         # optional, pass in desired log type for MSFT Sentinel
         "sentinel_customer_id": 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
         "sentinel_shared_key": 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx==',
         "sentinel_log_type": 'WebMonitorTest'
      },
)
```

## Quick Start with Python

You can look at our example Python script `direct_to_api/send_logs.py`. It shows you how to batch JSON data into 6mb chunks and send it to our API. You will need an API token from <https://cwolves.com/dashboard/api-tokens/> to use this script.
