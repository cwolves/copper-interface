# Copper Interface

Copper allows you to send your logs to a single endpoint to be deduplicated and aggregated intelligently. Optionally, Copper can be configured to forward logs to a Splunk HEC or Sentinel Log Analytics workspace.

This repository contains infrastructure as code, examples, and an API specification to quickly get started with the Copper API.

In summary, to use our API:

1. Gather your JSON Log data, Windows Event Log data, or XML data.
2. Send it to our AWS Lambda based API ('https://zof5dm3d636vqsqssv65rhs5f40qhsde.lambda-url.us-west-2.on.aws/')

Below, you will find documentation on how to use our API. There are 3 ways to get started:

1. Use our API _directly_ by sending a POST request to our API. ([API Guide](./direct_to_api/README.md))
2. Use Terraform to quickly create a stack in your AWS account. This will create a bucket in AWS that will forward log data from files to our API. ([Terraform Guide](./terraform/README.md))
3. Use the AWS CDK to quickly create a stack in your AWS account. This will create a bucket in AWS that will forward log data from files to our API. ([AWS CDK Guide](./aws_cdk/README.md))

For any support, feature requests, or suggestions reach out to thatcher@cwolves.com. We respond quickly!

## What happens to my logs?

This section discuss the tangible changes to your data when you send it to our API.

Our technology finds similarity between logs and groups them together. Here is a simple example.

You pass in 3 XML logs:

```xml
   <Event>
    <System>
      <Provider Name="ADWS" />
      <EventID Qualifiers="16384">1000</EventID>
      <Level>4</Level>
      <Task>1</Task>
      <Keywords>0x80000000000000</Keywords>
      <TimeCreated SystemTime="2023-02-03 18:43:22.1920779" />
      <EventRecordID>1</EventRecordID>
      <Channel>Active Directory Web Services</Channel>
      <Computer>AE01LAB-SECSVR01.loggingtest.com</Computer>
      <Security />
    </System>
    <EventData>
      <Data />
      <Binary />
    </EventData>
  </Event>
  <Event>
    <System>
      <Provider Name="ADWS" />
      <EventID Qualifiers="16384">1100</EventID>
      <Level>4</Level>
      <Task>2</Task>
      <Keywords>0x80000000000000</Keywords>
      <TimeCreated SystemTime="2023-02-03 18:43:23.3483328" />
      <EventRecordID>2</EventRecordID>
      <Channel>Active Directory Web Services</Channel>
      <Computer>AE01LAB-SECSVR01.loggingtest.com</Computer>
      <Security />
    </System>
    <EventData>
      <Data />
      <Binary />
    </EventData>
  </Event>
  <Event>
    <System>
      <Provider Name="ADWS" />
      <EventID Qualifiers="16384">1008</EventID>
      <Level>4</Level>
      <Task>1</Task>
      <Keywords>0x80000000000000</Keywords>
      <TimeCreated SystemTime="2023-02-03 18:43:23.3639578" />
      <EventRecordID>3</EventRecordID>
      <Channel>Active Directory Web Services</Channel>
      <Computer>AE01LAB-SECSVR01.loggingtest.com</Computer>
      <Security />
    </System>
    <EventData>
      <Data />
      <Binary />
    </EventData>
  </Event>
```

Our algorithm will output this data aggregated in JSON format.

```json
{
  "provider_name_count": {
    "ADWS": 3
  },
  "event_id_unique": [1000, 1100, 1008],
  "level_count": {
    "4": 3
  },
  "task_count": {
    "1": 2,
    "2": 1
  },
  "keywords_unique": ["0x80000000000000"],
  "timestamp_range": [
    "2023-02-03 18:43:22.1920779",
    "2023-02-03 18:43:23.3639578"
  ],
  "event_record_id_unique": [1, 2, 3],
  "channel_unique": ["Active Directory Web Services"],
  "security_unique": [null],
  "user_data_unique": ["{}"],
  "computer_group_by": "AE01LAB-SECSVR01.loggingtest.com",
  "logslash": 3
}
```

1. Data is transformed to JSON.
2. Headers are normalized and their merging strategy is appended to the header.
3. Data is grouped together based on similarity. Fields grouped together are transformed into a list or sometimes JSON objects based on their merging strategy.
4. The field `logslash` is added and represents the number of logs that were grouped together.

## Configuration

Out of the box, our technology requires no configuration. It simply _does its best_.

However, we offer you the ability to configure how logs are grouped.
