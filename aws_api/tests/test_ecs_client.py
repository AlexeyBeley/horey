"""
Testing ecs client.

"""

import os

from unittest.mock import Mock

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


def test_register_task_definition():
    client = ECSClient()
    client.provision_ecs_task_definition(dict_register_td_request)


CLUSTER_NAME = "my-cluster-name"
dict_create_cluster_request = {
    "clusterName": CLUSTER_NAME,
    "capacityProviders": ["FARGATE"],
}


def test_create_cluster():
    client = ECSClient()
    client.client.create_cluster(dict_create_cluster_request)


def test_run_task():
    ALLOWED_SUBNETS = []
    SECURITY_GROUPS = []
    dict_run_task_request = {
        "cluster": CLUSTER_NAME,
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
    client = ECSClient()
    client.run_task(dict_run_task_request)


def test_provision_capacity_provider():
    ecs_client = ECSClient()
    auto_scaling_group = Mock()
    auto_scaling_group.arn = mock_values["auto_scaling_group.arn"]
    tags = [{"key": "lvl", "value": "tst"}]
    capacity_provider = ECSCapacityProvider({})
    capacity_provider.name = "test-capacity-provider"
    capacity_provider.tags = tags
    capacity_provider.region = AWSAccount.get_aws_region()
    capacity_provider.tags.append({"key": "Name", "value": capacity_provider.name})

    capacity_provider.auto_scaling_group_provider = {
        "autoScalingGroupArn": auto_scaling_group.arn,
        "managedScaling": {
            "status": "ENABLED",
            "targetCapacity": 70,
            "minimumScalingStepSize": 1,
            "maximumScalingStepSize": 10000,
            "instanceWarmupPeriod": 300,
        },
        "managedTerminationProtection": "DISABLED",
    }
    ecs_client.provision_capacity_provider(capacity_provider)
    assert capacity_provider._arn is not None


def test_provision_cluster():
    tags = [{"key": "lvl", "value": "tst"}]

    ecs_client = ECSClient()
    cluster = ECSCluster({})
    cluster.region = AWSAccount.get_aws_region()
    cluster.settings = [{"name": "containerInsights", "value": "enabled"}]

    cluster.name = "test_cluster"
    cluster.tags = tags
    cluster.tags.append({"key": "Name", "value": cluster.name})
    cluster.configuration = {}
    cluster.capacity_providers = ["test-capacity-provider"]
    cluster.default_capacity_provider_strategy = [
        {"capacityProvider": "test-capacity-provider", "weight": 1, "base": 0}
    ]

    ecs_client.provision_cluster(cluster)

    assert cluster.arn is not None


def test_provision_service_with_tg():
    region = Region.get_region("us-west-2")
    ecs_client = ECSClient()
    ecs_task_definition = Mock()
    ecs_task_definition.arn = mock_values["ecs_task_definition.arn"]
    ecs_cluster = Mock()
    ecs_cluster.arn = mock_values["ecs_cluster.arn"]
    target_group = Mock()
    target_group.arn = mock_values["target_group.arn"]
    service_name = mock_values["service_name"]
    container_name = mock_values["container_name"]
    role_arn = mock_values["ecs_service.role_arn"]
    ecs_service = ECSService({})
    ecs_service.region = region

    ecs_service.tags = [
        {"key": "env", "value": "test"},
        {"key": "Name", "value": "test"},
    ]

    ecs_service.name = service_name
    ecs_service.cluster_arn = ecs_cluster.arn
    ecs_service.task_definition = ecs_task_definition.arn
    ecs_service.load_balancers = [
        {
            "targetGroupArn": target_group.arn,
            "containerName": container_name,
            "containerPort": 443,
        }
    ]
    ecs_service.desired_count = 1

    ecs_service.launch_type = "EC2"

    ecs_service.role_arn = role_arn
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

    ecs_client.provision_service(ecs_service)


def test_provision_service_without_tg():
    region = Region.get_region("us-west-2")
    ecs_client = ECSClient()
    ecs_task_definition = Mock()
    ecs_task_definition.arn = mock_values["ecs_task_definition.arn"]
    ecs_cluster = Mock()
    ecs_cluster.arn = mock_values["ecs_cluster.arn"]
    service_name = mock_values["service_name"]
    role_arn = mock_values["ecs_service.role_arn"]
    ecs_service = ECSService({})
    ecs_service.region = region

    ecs_service.tags = [
        {"key": "env", "value": "test"},
        {"key": "Name", "value": "test"},
    ]

    ecs_service.name = service_name
    ecs_service.cluster_arn = ecs_cluster.arn
    ecs_service.task_definition = ecs_task_definition.arn

    ecs_service.desired_count = 30

    ecs_service.launch_type = "EC2"

    ecs_service.role_arn = role_arn
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

    ecs_client.provision_service(ecs_service)


def test_get_all_task_definitions():
    client = ECSClient()
    ret = client.get_all_task_definitions(region=Region.get_region("us-east-1"))
    assert isinstance(ret, list)

def test_dispose_cluster():
    assert True

if __name__ == "__main__":
    # test_register_task_definition()
    # test_provision_cluster()
    # test_provision_service_without_tg()
    # test_get_all_task_definitions()
    # test_dispose_cluster()
    test_dispose_cluster()
