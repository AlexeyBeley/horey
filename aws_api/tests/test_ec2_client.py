import os
import sys
import json
import pdb

sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(0, "~/private/aws_api/ignore")
sys.path.insert(0, "~/private/aws_api/src/base_entities")
sys.path.insert(0, "~/private/aws_api/src/aws_clients")

from ec2_client import EC2Client
import ignore_me
import logging

logger = logging.Logger(__name__)
from horey.aws_api.base_entities.aws_account import AWSAccount

tested_account = ignore_me.acc_default
AWSAccount.set_aws_account(tested_account)

cache_base_path = os.path.join(os.path.expanduser("~"), f"private/aws_api/ignore/cache_objects_{tested_account.name}")


def test_init_ec2_client():
    assert isinstance(EC2Client(), EC2Client)


DICT_CREATE_SECURITY_GROUP_REQUEST = {
    "Description": "ECS task access from web",
    "GroupName": "ecs-task-security-group1",
}


def test_create_security_group():
    client = EC2Client()
    client.create_security_group(DICT_CREATE_SECURITY_GROUP_REQUEST)


SECURITY_GROUP_ID = ""
DICT_AUTHORIZE_SECURITY_GROUP_INGRESS_REQUEST = {
      "GroupId": SECURITY_GROUP_ID,
        "IpPermissions":[
            {'IpProtocol': 'tcp',
             'FromPort': 8080,
             'ToPort': 8080,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
        ]}


def test_authorize_security_group_ingress():
    client = EC2Client()
    client.authorize_security_group_ingress(DICT_AUTHORIZE_SECURITY_GROUP_INGRESS_REQUEST)


if __name__ == "__main__":
    #test_create_security_group()
    test_authorize_security_group_ingress()

