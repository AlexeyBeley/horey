import os
import sys
import json
import pdb
from unittest.mock import Mock


from horey.aws_api.aws_clients.iam_client import IamClient
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.aws_api.aws_services_entities.iam_role import IamRole


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
    "MaxSessionDuration": 12 * 60 * 60
}


def test_create_role():
    client = IamClient()
    client.create_role(DICT_ECS_EXECUTION_ROLE_REQUEST)


DICT_ATTACH_POLICY_REQUEST = {
    "PolicyArn": "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
    "RoleName": ECS_EXECUTION_ROLE_NAME
}


def test_attach_role_policy_raw():
    client = IamClient()
    client.attach_role_policy_raw(DICT_ATTACH_POLICY_REQUEST)


DICT_TRUST_LAMBDA = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}


def test_provision_role():
    role = IamRole({})
    role.name = "role-alexey-test-lambda"
    role.assume_role_policy_document = json.dumps(DICT_TRUST_LAMBDA)
    role.description = "Alexey test role"
    role.max_session_duration = 12 * 60 * 60

    policy = Mock()
    policy.arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"

    role.policies = [policy]

    client = IamClient()
    client.provision_iam_role(role)


if __name__ == "__main__":
    test_provision_role()
