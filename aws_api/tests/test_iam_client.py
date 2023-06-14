# pylint: skip-file
import json
from unittest.mock import Mock


from horey.aws_api.aws_clients.iam_client import IamClient
from horey.aws_api.aws_services_entities.iam_role import IamRole
from horey.aws_api.aws_services_entities.iam_policy import IamPolicy
from horey.aws_api.aws_services_entities.iam_instance_profile import IamInstanceProfile
from horey.aws_api.aws_services_entities.iam_user import IamUser


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
    client.create_role(DICT_ECS_EXECUTION_ROLE_REQUEST)


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


def test_provision_instance_profile():
    iam_instance_profile = IamInstanceProfile({})
    iam_instance_profile.name = "profile-alexey-test"
    iam_instance_profile.tags = [{"Key": "Name", "Value": iam_instance_profile.name}]
    iam_instance_profile.roles = [{"RoleName": "role-alexey-test-lambda"}]

    client = IamClient()
    client.provision_instance_profile(iam_instance_profile)


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
                    f"arn:aws:logs:*:12345678910:log-group:horey-test"
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
                    f"arn:aws:logs:*:12345678910:log-group:horey-test"
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


def test_provision_user():
    user = IamUser({"UserName": "test-user"})
    user.tags = [{"Key": "Name", "Value": user.name}]
    client = IamClient()
    client.provision_user(user)


def test_dispose_user():
    user = IamUser({"UserName": "test-user"})
    client = IamClient()
    client.dispose_user(user)


if __name__ == "__main__":
    # test_provision_role()
    # test_provision_instance_profile()
    # test_provision_policy()
    # test_provision_change_policy()
    test_provision_user()
    test_dispose_user()
