# AWS_API configuration

## Q/A
- Why using .py files and not .json or .yaml?
- Short answer: Because you can use code to hide "assume_role" and "external_id" values.
- Long answer: You can use any type of configuration file. 
  Thanks to ConfigurationPolicy idea you can feed it ith values from any supported source, 
  while the evaluation logic is common to all.

This document explains how to manage multiple accounts/regions using single AWS_API installation.
AWSAccount is not the AWS Account as you know it. This is a data structure used to manage single connection.
Several AWSAccounts can point the same AWS Accounts' different regions.

## Sample configuration values file
`aws_api/tests/configuration_values.py`
## Sample accounts file
`aws_api/tests/accounts/managed_accounts.py`


## Components
### AWSAccount
This is an environment managed with the same session. 
There can be different logical environments inside (like STG and PROD), 
but if you connect once to manage them all - they must be stored in a single AWSAccount.

### AWSAccount.ConnectionStep
Single step in a chain while connecting the environment. 
There are different mechanisms one can use to restrict access to a management role.
Currently, 2 available: 
* Using AWS profile name.
```python
AWSAccount.ConnectionStep({"profile": "horey_account", "region_mark": "us-east-1"})
```
* Using assume role mechanism.
```python
AWSAccount.ConnectionStep({"assume_role": "arn:aws:iam::109876543210:role/sts-management-role"})
```
or with external id:
```python
AWSAccount.ConnectionStep({"assume_role": f"arn:aws:iam::{acc_staging.id}:role/sts-ec2-management-role", "external_id": "ABCDE123456"})
```

### Region
AWS region to fetch the data from.
Each region must be explicitly set.
```python
reg = Region()
reg.region_mark = "us-east-1"
acc_staging.regions[reg.region_mark] = reg
```
