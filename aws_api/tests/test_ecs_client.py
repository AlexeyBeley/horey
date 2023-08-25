"""
Testing ecs client.

"""

import os

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

SERVICE_NAME = "tes-service-name"
TEST_CLUSTER_NAME = "test-cluster"
CAPACITY_PROVIDER_NAME ="test-capacity-provider"

class Dependencies:
    """
    Collected during the runtime.

    """

    fargate_task_definition_arn = None
    cluster_arn = None


def create_task_definition():
    td = ECSTaskDefinition(dict_register_td_request)
    td.region = region
    td.tags = tags
    client.provision_ecs_task_definition(td)
    return td


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


@pytest.mark.skip()
def test_register_task_definition():
    td = ECSTaskDefinition(dict_register_td_request)
    td.region = region
    td.tags = tags
    client.provision_ecs_task_definition(td)
    return td

@pytest.mark.skip()
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
    client.run_task(dict_run_task_request)


#@pytest.mark.skip()
def test_provision_capacity_provider():
    auto_scaling_group = Mock()
    auto_scaling_group.arn = mock_values["auto_scaling_group.arn"]
    capacity_provider = ECSCapacityProvider({})
    capacity_provider.name = CAPACITY_PROVIDER_NAME
    capacity_provider.tags = tags
    capacity_provider.region = region
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
    client.provision_capacity_provider(capacity_provider)
    assert capacity_provider._arn is not None


#@pytest.mark.skip()
def test_provision_cluster():
    cluster = ECSCluster({})
    cluster.region = region
    cluster.settings = [{"name": "containerInsights", "value": "enabled"}]

    cluster.name = TEST_CLUSTER_NAME
    cluster.tags = tags
    cluster.tags.append({"key": "Name", "value": cluster.name})
    cluster.configuration = {}
    cluster.capacity_providers = [CAPACITY_PROVIDER_NAME]
    cluster.default_capacity_provider_strategy = [
        {"capacityProvider": CAPACITY_PROVIDER_NAME, "weight": 1, "base": 0}
    ]

    client.provision_cluster(cluster)
    Dependencies.cluster_arn = cluster.arn

    assert cluster.arn is not None

def test_task_definition():
    Dependencies.fargate_task_definition_arn = create_task_definition().arn
    assert Dependencies.fargate_task_definition_arn is not None

#@pytest.mark.skip()
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
    ecs_service.network_configuration =  {
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

    #ecs_service.role_arn = role_arn
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

#@pytest.mark.skip()
def test_dispose_service_with_tg():
    ecs_service = ECSService({})
    ecs_service.name = SERVICE_NAME
    ecs_service.region = region
    ecs_cluster = Mock()
    ecs_cluster.name = TEST_CLUSTER_NAME
    ecs_cluster.arn = mock_values["ecs_cluster.arn"]
    client.dispose_service(ecs_cluster, ecs_service)


@pytest.mark.skip()
def test_provision_service_without_tg():
    ecs_client = ECSClient()
    ecs_task_definition = Mock()
    ecs_task_definition.arn = mock_values["ecs_task_definition.arn"]
    ecs_cluster = Mock()
    ecs_cluster.arn = mock_values["ecs_cluster.arn"]
    role_arn = mock_values["ecs_service.role_arn"]
    ecs_service = ECSService({})
    ecs_service.region = region

    ecs_service.tags = tags

    ecs_service.name = SERVICE_NAME
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

@pytest.mark.skip()
def test_get_all_task_definitions():
    ret = client.get_all_task_definitions(region=Region.get_region("us-east-1"))
    assert isinstance(ret, list)

@pytest.mark.skip()
def test_dispose_cluster():
    assert True

if __name__ == "__main__":
    test_provision_cluster()
    # test_provision_service_with_tg()
    # test_register_task_definition()
    # test_provision_cluster()
    # test_provision_service_without_tg()
    # test_get_all_task_definitions()
    # test_dispose_service_without_tg()
    # test_dispose_cluster()
