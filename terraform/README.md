# Quick Start using Terraform

We've just added this, please let us know if you have any issues.

You should be comfortable working with Terraform.

## Overview

There is a Terraform script `deploy_logslash.tf` which defines the resources that will be created in your AWS account.

## Prerequisites

- Terraform [Install](https://learn.hashicorp.com/tutorials/terraform/install-cli)
- AWS Account [Sign Up](https://aws.amazon.com/)
- Splunk HEC Endpoint [Guide](https://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector)

## Instructions

0. Prerequisites
   [Sign Up](https://cwolves.com) for a Cwolves Account
1. Clone this repository onto your local machine.

   `git clone git@github.com:arctype-dev/copper-interface.git`

2. Change into the directory.

   `cd copper-interface/terraform`

3. Initialize Terraform. This creates a stack with the resources required to deploy a stack via Terraform. You can see the stack in CloudFormation.

   `terraform init`

4. Deploy the stack. This creates the resources in your AWS account. You can see the stack in CloudFormation.

   `terraform apply`
