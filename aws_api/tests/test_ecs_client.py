"""
Testing ecs client.

"""

import os
import json

from unittest.mock import Mock
import pytest

from horey.aws_api.aws_clients.ecs_client import ECSClient
from horey.aws_api.aws_services_entities.ecs_capacity_provider import (
    ECSCapacityProvider,
)
from horey.aws_api.aws_services_entities.ecs_cluster import ECSCluster
from horey.aws_api.aws_services_entities.ecs_service import ECSService
from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.common_utils.common_utils import CommonUtils
from horey.aws_api.aws_services_entities.ecs_task_definition import ECSTaskDefinition
from horey.aws_api.aws_services_entities.auto_scaling_group import AutoScalingGroup
from horey.aws_api.aws_services_entities.iam_role import IamRole
from horey.aws_api.aws_services_entities.iam_instance_profile import IamInstanceProfile
from horey.aws_api.aws_services_entities.ec2_launch_template import EC2LaunchTemplate

from horey.aws_api.aws_clients.auto_scaling_client import AutoScalingClient
from horey.aws_api.aws_clients.ssm_client import SSMClient
from horey.aws_api.aws_clients.ec2_client import EC2Client
from horey.aws_api.aws_clients.iam_client import IamClient

configuration_values_file_full_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py"
)
logger = get_logger(
    configuration_values_file_full_path=configuration_values_file_full_path
)

accounts_file_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "..",
        "ignore",
        "accounts",
        "managed_accounts.py",
    )
)

accounts = CommonUtils.load_object_from_module(accounts_file_full_path, "main")
AWSAccount.set_aws_account(accounts["dev"])

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

# pylint: disable= missing-function-docstring

region = Region.get_region("us-west-2")

tags = [{"key": "lvl", "value": "tst"}]

client = ECSClient()

SERVICE_NAME = "test-service-name"
TEST_CLUSTER_NAME = "test-cluster"
CAPACITY_PROVIDER_NAME = "test-capacity-provider"
AUTOSCALING_GROUP_NAME = "asg_test_ecs_cluster"
TEST_CONTAINER_INSTANCE_IAM_ROLE = "test_role_container_instance"
TEST_CONTAINER_INSTANCE_IAM_PROFILE_NAME = "test_iam_profile_container_instance"
TEST_LAUNCH_TEMPLATE_NAME = "test_launch_template"


class Dependencies:
    """
    Collected during the runtime.

    """

    fargate_task_definition_arn = None
    cluster_arn = None
    autoscaling_group_arn = None


@pytest.mark.skip
def create_task_definition():
    td = ECSTaskDefinition(dict_register_td_request)
    td.region = region
    td.tags = tags
    client.provision_ecs_task_definition(td)
    return td


@pytest.mark.skip
def test_init_ecs_client():
    assert isinstance(ECSClient(), ECSClient)


CONTAINER_NAME = "test-container-name"
IMAGE_URL = mock_values["image_ecr_url"]
CPU_SIZE = 512
MEMORY_SIZE = 1024
CONTAINER_PORT = 8080
HOST_PORT = 8080
TASK_DEFINITION_FAMILY = "task-definition-family"

EXECUTION_ROLE_ARN = mock_values["ecs_task_execution_role_arn"]
dict_register_td_request = {
    "family": TASK_DEFINITION_FAMILY,
    "executionRoleArn": EXECUTION_ROLE_ARN,
    "requiresCompatibilities": ["FARGATE"],
    "networkMode": "awsvpc",
    "cpu": str(CPU_SIZE),
    "memory": str(MEMORY_SIZE),
    "containerDefinitions": [
        {
            "name": CONTAINER_NAME,
            "image": IMAGE_URL,
            "portMappings": [
                {
                    "containerPort": CONTAINER_PORT,
                    "hostPort": HOST_PORT,
                    "protocol": "tcp",
                },
            ],
            "essential": True,
        },
    ],
}


@pytest.mark.skip
def test_register_task_definition():
    td = ECSTaskDefinition(dict_register_td_request)
    td.region = region
    td.tags = tags
    client.provision_ecs_task_definition(td)
    return td


@pytest.mark.skip
def test_run_task():
    ALLOWED_SUBNETS = []
    SECURITY_GROUPS = []
    dict_run_task_request = {
        "cluster": TEST_CLUSTER_NAME,
        "taskDefinition": TASK_DEFINITION_FAMILY,
        "launchType": "FARGATE",
        "networkConfiguration": {
            "awsvpcConfiguration": {
                "subnets": ALLOWED_SUBNETS,
                "securityGroups": SECURITY_GROUPS,
                "assignPublicIp": "ENABLED",
            }
        },
    }
    client.run_task(region, dict_run_task_request)


@pytest.mark.skip
def provision_container_instance_iam_profile():
    assume_role_policy = """{
            "Version": "2012-10-17",
            "Statement": [
            {
            "Effect": "Allow",
            "Principal": {
            "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
            }
            ]
            }"""

    iam_role = IamRole({})
    iam_role.name = TEST_CONTAINER_INSTANCE_IAM_ROLE
    iam_role.assume_role_policy_document = assume_role_policy
    iam_role.description = TEST_CONTAINER_INSTANCE_IAM_ROLE
    iam_role.max_session_duration = 3600
    iam_role.tags = [{
        "Key": "Name",
        "Value": iam_role.name
    }]

    iam_client = IamClient()
    iam_role.path = "/test/"
    iam_client.provision_role(iam_role)

    iam_instance_profile = IamInstanceProfile({})
    iam_instance_profile.name = TEST_CONTAINER_INSTANCE_IAM_PROFILE_NAME
    iam_instance_profile.tags = [{
        "Key": "Name",
        "Value": iam_instance_profile.name
    }]
    iam_instance_profile.roles = [{"RoleName": iam_role.name}]
    iam_client.provision_instance_profile(iam_instance_profile)
    return iam_instance_profile


@pytest.mark.skip
def provision_launch_template():
    ssm_client = SSMClient()
    param = ssm_client.get_region_parameter(region,
                                            "/aws/service/ecs/optimized-ami/amazon-linux-2/recommended")

    filter_request = {"ImageIds": [json.loads(param.value)["image_id"]]}
    ec2_client = EC2Client()
    amis = ec2_client.get_region_amis(region, custom_filters=filter_request)
    if len(amis) > 1:
        raise RuntimeError(f"Can not find single AMI using filter: {filter_request['Filters']}")
    ami = amis[0]

    with open("./user_data_tmp.sh", "w", encoding="utf-8") as file_handler:
        file_handler.write(f'#!/bin/bash\n\
                             echo "ECS_CLUSTER={TEST_CLUSTER_NAME}" >> /etc/ecs/ecs.config')

    user_data = ec2_client.generate_user_data_from_file("./user_data_tmp.sh")
    profile = provision_container_instance_iam_profile()

    launch_template = EC2LaunchTemplate({})
    launch_template.name = TEST_LAUNCH_TEMPLATE_NAME
    launch_template.tags = [{
        "Key": "Name",
        "Value": launch_template.name
    }]
    launch_template.region = region

    launch_template.launch_template_data = {"EbsOptimized": False,
                                            "IamInstanceProfile": {
                                                "Arn": profile.arn
                                            },
                                            "BlockDeviceMappings": [
                                                {
                                                    "DeviceName": "/dev/xvda",
                                                    "Ebs": {
                                                        "VolumeSize": 30,
                                                        "VolumeType": "gp3"
                                                    }
                                                }
                                            ],
                                            "ImageId": ami.id,
                                            "InstanceType": "t3a.small",
                                            "KeyName": mock_values["container_instance_ssh_key_name"],
                                            "Monitoring": {
                                                "Enabled": True
                                            },
                                            "NetworkInterfaces": [
                                                {
                                                    "AssociatePublicIpAddress": True,
                                                    "DeleteOnTermination": True,
                                                    "DeviceIndex": 0,
                                                    "Groups": mock_values["ecs_fargate_service_security_groups"]
                                                },
                                            ],
                                            "UserData": user_data
                                            }
    EC2Client().provision_launch_template(launch_template)
    return launch_template


@pytest.mark.skip
def provision_autoscaling_group():
    launch_template = provision_launch_template()
    group = AutoScalingGroup({})
    group.region = region
    group.name = AUTOSCALING_GROUP_NAME
    group.tags = [{"Key": "lvl", "Value": "tst"}]
    group.launch_template = {
        "LaunchTemplateId": launch_template.id,
        "Version": "$Default"
    }
    group.min_size = 0
    group.max_size = 0
    group.desired_capacity = 0
    group.vpc_zone_identifier = ",".join(mock_values["ecs_fargate_service_subnets"])
    AutoScalingClient().provision_auto_scaling_group(group)
    Dependencies.autoscaling_group_arn = group.arn


@pytest.mark.skip
def test_provision_capacity_provider():
    if Dependencies.autoscaling_group_arn is None:
        provision_autoscaling_group()

    capacity_provider = ECSCapacityProvider({})
    capacity_provider.name = CAPACITY_PROVIDER_NAME
    capacity_provider.tags = tags
    capacity_provider.region = region
    capacity_provider.tags.append({"key": "Name", "value": capacity_provider.name})

    capacity_provider.auto_scaling_group_provider = {
        "autoScalingGroupArn": Dependencies.autoscaling_group_arn,
        "managedScaling": {
            "status": "ENABLED",
            "targetCapacity": 70,
            "minimumScalingStepSize": 1,
            "maximumScalingStepSize": 10000,
            "instanceWarmupPeriod": 300,
        },
        "managedTerminationProtection": "DISABLED",
    }
    client.provision_capacity_provider(capacity_provider)
    assert capacity_provider.arn is not None


@pytest.mark.skip
def test_provision_cluster():
    cluster = ECSCluster({})
    cluster.region = region
    cluster.settings = [{"name": "containerInsights", "value": "enabled"}]

    cluster.name = TEST_CLUSTER_NAME
    cluster.tags = [{"key": "Name", "value": cluster.name}]
    cluster.configuration = {}
    cluster.capacity_providers = [CAPACITY_PROVIDER_NAME]
    cluster.default_capacity_provider_strategy = [
        {"capacityProvider": CAPACITY_PROVIDER_NAME, "weight": 1, "base": 0}
    ]

    client.provision_cluster(cluster)
    Dependencies.cluster_arn = cluster.arn

    assert cluster.arn is not None


@pytest.mark.skip
def test_task_definition():
    Dependencies.fargate_task_definition_arn = create_task_definition().arn
    assert Dependencies.fargate_task_definition_arn is not None


@pytest.mark.skip
def test_provision_service_with_tg():
    ecs_task_definition = Mock()
    ecs_task_definition.arn = Dependencies.fargate_task_definition_arn
    ecs_cluster = Mock()
    ecs_cluster.arn = Dependencies.cluster_arn
    target_group = Mock()
    target_group.arn = mock_values["target_group.arn"]
    container_name = CONTAINER_NAME
    ecs_service = ECSService({})
    ecs_service.region = region
    ecs_service.network_configuration = {
        "awsvpcConfiguration": {
            "subnets": mock_values["ecs_fargate_service_subnets"],
            "securityGroups": mock_values["ecs_fargate_service_security_groups"]
        }
    }

    ecs_service.tags = tags

    ecs_service.name = SERVICE_NAME
    ecs_service.cluster_arn = ecs_cluster.arn
    ecs_service.task_definition = ecs_task_definition.arn
    ecs_service.load_balancers = [
        {
            "targetGroupArn": target_group.arn,
            "containerName": container_name,
            "containerPort": CONTAINER_PORT,
        }
    ]
    ecs_service.desired_count = 1

    ecs_service.launch_type = "EC2"

    # ecs_service.role_arn = role_arn
    ecs_service.deployment_configuration = {
        "deploymentCircuitBreaker": {"enable": False, "rollback": False},
        "maximumPercent": 200,
        "minimumHealthyPercent": 100,
    }
    ecs_service.placement_strategy = [
        {"type": "spread", "field": "attribute:ecs.availability-zone"},
        {"type": "spread", "field": "instanceId"},
    ]
    ecs_service.health_check_grace_period_seconds = 10
    ecs_service.scheduling_strategy = "REPLICA"
    ecs_service.enable_ecs_managed_tags = False
    ecs_service.enable_execute_command = False
    client.provision_service(ecs_service, asyncronous=True)


@pytest.mark.skip
def test_dispose_service_with_tg():
    ecs_service = ECSService({})
    ecs_service.name = SERVICE_NAME
    ecs_service.region = region
    ecs_cluster = Mock()
    ecs_cluster.name = TEST_CLUSTER_NAME
    ecs_cluster.arn = mock_values["ecs_cluster.arn"]
    client.dispose_service(ecs_cluster, ecs_service)


@pytest.mark.skip
def test_dispose_capacity_provider():
    capacity_provider = ECSCapacityProvider({})
    capacity_provider.name = CAPACITY_PROVIDER_NAME
    capacity_provider.region = region

    response = client.dispose_capacity_provider(capacity_provider)
    assert response


@pytest.mark.skip
def test_get_all_task_definitions():
    ret = client.get_all_task_definitions(region=Region.get_region("us-east-1"))
    assert isinstance(ret, list)


@pytest.mark.skip
def test_dispose_cluster():
    assert True


@pytest.mark.wip
def test_yield_task_definitions_raw():
    ret = []
    for x in client.yield_task_definitions_raw(region=Region.get_region("us-west-2")):
        ret.append(x)
    assert isinstance(ret, list)
