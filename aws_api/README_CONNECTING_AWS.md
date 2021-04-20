#MANAGING AWS CONNECTIONS

##Sample configuration file
aws_api/tests/configuration_values.py
aws_api/tests/accounts/managed_accounts.py


##Components
###AWSAccount
This is an environment managed the same session. 
There can be different logical environments inside (like STG and PROD), 
but if you connect once to manage them all - they must be single AWSAccount.

###AWSAccount.ConnectionStep
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

###Region
AWS region to fetch the data from.
Each region must be explicitly set.
```python
reg = Region()
reg.region_mark = "us-east-1"
acc_staging.regions[reg.region_mark] = reg
```


