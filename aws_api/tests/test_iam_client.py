import os
import sys
import json
import pdb

sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(0, "/Users/alexeybe/private/IP/ip")
sys.path.insert(0, "/Users/alexeybe/private/aws_api/ignore")
sys.path.insert(0, "/Users/alexeybe/private/aws_api/src/base_entities")
sys.path.insert(0, "/Users/alexeybe/private/aws_api/src/aws_clients")

from iam_client import IamClient
import ignore_me
import logging
logger = logging.Logger(__name__)
from horey.aws_api.base_entities.aws_account import AWSAccount

tested_account = ignore_me.acc_default
AWSAccount.set_aws_account(tested_account)


cache_base_path = os.path.join(os.path.expanduser("~"), f"private/aws_api/ignore/cache_objects_{tested_account.name}")


def test_init_iam_client():
    assert isinstance(IamClient(), IamClient)


TRUST_PERMISSION = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
ECS_EXECUTION_ROLE_NAME = "HoreyEcsExecutionRole1"
DICT_ECS_EXECUTION_ROLE_REQUEST = {
    "RoleName": ECS_EXECUTION_ROLE_NAME,
    "AssumeRolePolicyDocument": json.dumps(TRUST_PERMISSION),
    "Description": "string",
    "MaxSessionDuration": 12*60*60
    }


def test_create_role():
    client = IamClient()
    client.create_role(DICT_ECS_EXECUTION_ROLE_REQUEST)


DICT_ATTACH_POLICY_REQUEST= {
    "PolicyArn": "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
    "RoleName": ECS_EXECUTION_ROLE_NAME
}


def test_attach_role_policy():
    client = IamClient()
    client.attach_role_policy(DICT_ATTACH_POLICY_REQUEST)


if __name__ == "__main__":
    test_attach_role_policy()
