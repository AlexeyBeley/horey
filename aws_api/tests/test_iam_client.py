"""
Test IAM client.

"""
import os
import json
import pytest


from horey.aws_api.aws_clients.iam_client import IamClient
from horey.aws_api.aws_services_entities.iam_role import IamRole
from horey.aws_api.aws_services_entities.iam_policy import IamPolicy
from horey.aws_api.aws_services_entities.iam_instance_profile import IamInstanceProfile
from horey.aws_api.aws_services_entities.iam_user import IamUser

IamClient().main_cache_dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..",
            "ignore",
            "cache"
        )
    )
# pylint: disable= missing-function-docstring

@pytest.mark.todo
def test_init_iam_client():
    assert isinstance(IamClient(), IamClient)


TRUST_PERMISSION = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {"Service": "ecs-tasks.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }
    ],
}
ECS_EXECUTION_ROLE_NAME = "HoreyEcsExecutionRole1"
DICT_ECS_EXECUTION_ROLE_REQUEST = {
    "RoleName": ECS_EXECUTION_ROLE_NAME,
    "AssumeRolePolicyDocument": json.dumps(TRUST_PERMISSION),
    "Description": "string",
    "MaxSessionDuration": 12 * 60 * 60,
}


def test_create_role():
    client = IamClient()
    client.provision_role(DICT_ECS_EXECUTION_ROLE_REQUEST)


DICT_ATTACH_POLICY_REQUEST = {
    "PolicyArn": "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
    "RoleName": ECS_EXECUTION_ROLE_NAME,
}


def test_attach_role_policy_raw():
    client = IamClient()
    client.attach_role_policy_raw(DICT_ATTACH_POLICY_REQUEST)


DICT_TRUST_LAMBDA = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }
    ],
}

@pytest.mark.todo
def test_provision_instance_profile():
    iam_instance_profile = IamInstanceProfile({})
    iam_instance_profile.name = "profile-alexey-test"
    iam_instance_profile.tags = [{"Key": "Name", "Value": iam_instance_profile.name}]
    iam_instance_profile.roles = [{"RoleName": "role-alexey-test-lambda"}]

    client = IamClient()
    client.provision_instance_profile(iam_instance_profile)

@pytest.mark.todo
def test_provision_policy():
    policy = IamPolicy({})
    policy.document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "logs:CreateLogStream",
                ],
                "Resource": [
                    "arn:aws:logs:*:12345678910:log-group:horey-test"
                ],
                "Effect": "Allow"
            }
        ]
    }
    policy.document = json.dumps(policy.document)
    policy.name = "pol-test-provision"
    policy.description = "pol-test-provision"
    policy.tags = [{
        "Key": "Name",
        "Value": policy.name
    }]

    client = IamClient()
    client.provision_policy(policy)

@pytest.mark.todo
def test_provision_change_policy():
    policy = IamPolicy({})
    policy.document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "logs:CreateLogStream",
                    "logs:CreateLogGroup"
                ],
                "Resource": [
                    "arn:aws:logs:*:12345678910:log-group:horey-test"
                ],
                "Effect": "Allow"
            }
        ]
    }
    policy.document = json.dumps(policy.document)
    policy.name = "pol-test-provision"
    policy.description = "pol-test-provision"
    policy.tags = [{
        "Key": "Name",
        "Value": policy.name
    }]

    client = IamClient()
    client.provision_policy(policy)


@pytest.mark.todo
def test_provision_user():
    user = IamUser({"UserName": "test-user"})
    user.tags = [{"Key": "Name", "Value": user.name}]
    client = IamClient()
    client.provision_user(user)

@pytest.mark.todo
def test_dispose_user():
    user = IamUser({"UserName": "test-user"})
    client = IamClient()
    client.dispose_user(user)

@pytest.mark.done
def test_yield_roles():
    client = IamClient()
    role = None
    for role in client.yield_roles(update_info=False, filters_req=None, full_information=True):
        break
    assert role.arn is not None

@pytest.mark.done
def test_get_all_roles_full_info_true():
    client = IamClient()
    ret = client.get_all_roles(full_information=True)
    assert len(ret) > 0


@pytest.mark.done
def test_get_all_roles_full_info_false():
    client = IamClient()
    ret = client.get_all_roles(full_information=False)
    assert len(ret) > 0

role_name = "role-test-provision"

@pytest.mark.todo
def test_provision_role_create():
    role = IamRole({})
    role.path = "/test/"
    role.name = role_name
    role.assume_role_policy_document = json.dumps(DICT_TRUST_LAMBDA)
    role.description = "Alexey test role"
    role.max_session_duration = 12 * 60 * 60

    role.managed_policies_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"]

    client = IamClient()
    client.provision_role(role)

@pytest.mark.todo
def test_provision_role_update():
    role = IamRole({})
    role.path = "/test/"
    role.name = role_name
    role.assume_role_policy_document = json.dumps(DICT_TRUST_LAMBDA)
    role.description = "Alexey test role1"
    role.max_session_duration = 10 * 60 * 60

    role.managed_policies_arns = []

    client = IamClient()
    client.provision_role(role)

@pytest.mark.todo
def test_provision_role_create_inline_policy():
    policy = IamPolicy({})
    policy.document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "logs:CreateLogStream",
                ],
                "Resource": [
                    "arn:aws:logs:*:12345678910:log-group:horey-test"
                ],
                "Effect": "Allow"
            }
        ]
    }
    policy.name = "pol-test-provision"

    client = IamClient()
    role = IamRole({})
    role.path = "/test/"
    role.name = role_name
    role.inline_policies.append(policy)
    client.provision_role(role)


@pytest.mark.todo
def test_provision_role_update_inline_policy():
    policy = IamPolicy({})
    policy.document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "logs:CreateLogStream",
                ],
                "Resource": [
                    "arn:aws:logs:us-west-2:12345678910:log-group:horey-test"
                ],
                "Effect": "Allow"
            }
        ]
    }
    policy.name = "pol-test-provision"

    client = IamClient()
    role = IamRole({})
    role.path = "/test/"
    role.name = role_name
    role.inline_policies.append(policy)
    client.provision_role(role)


@pytest.mark.todo
def test_provision_role_delete_inline_policy():
    client = IamClient()
    role = IamRole({})
    role.path = "/test/"
    role.name = role_name
    role.inline_policies = []
    client.provision_role(role)


@pytest.mark.todo
def test_dispose_role():
    role = IamRole({})
    role.path = "/test/"
    role.name = role_name
    client = IamClient()
    client.dispose_role(role)
