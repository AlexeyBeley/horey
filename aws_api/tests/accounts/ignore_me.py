import sys
import os
import pdb
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region

# DEFAULT
acc_default = AWSAccount()
acc_default.name = "default_account"
acc_default.id = "12345678910"
cs1 = AWSAccount.ConnectionStep({"profile": "default", "region_mark": "us-east-1"})
acc_default.connection_steps.append(cs1)
reg = Region()
reg.region_mark = "us-east-1"
acc_default.regions[reg.region_mark] = reg
reg = Region()
reg.region_mark = "us-west-2"
acc_default.regions[reg.region_mark] = reg

# STAGING
acc_staging = AWSAccount()
acc_staging.name = "staging_account"
acc_staging.id = "109876543210"

cs1 = AWSAccount.ConnectionStep({"profile": "default", "region_mark": "us-east-1"})
cs2 = AWSAccount.ConnectionStep({"assume_role": "arn:aws:iam::109876543210:role/sts-management-role"})
cs3 = AWSAccount.ConnectionStep({"assume_role": f"arn:aws:iam::{acc_staging.id}:role/sts-ec2-management-role", "external_id": "ABCDE123456"})

acc_staging.connection_steps.append(cs1)
acc_staging.connection_steps.append(cs2)
acc_staging.connection_steps.append(cs3)

reg = Region()
reg.region_mark = "us-east-1"
acc_staging.regions[reg.region_mark] = reg

reg = Region()
reg.region_mark = "us-west-2"
acc_staging.regions[reg.region_mark] = reg
