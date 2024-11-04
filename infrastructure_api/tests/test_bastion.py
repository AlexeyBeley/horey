"""
Init and cache AWS objects.

"""

from pathlib import Path

import pytest
from horey.aws_api.aws_api import AWSAPI
from horey.h_logger import get_logger
from horey.infrastructure_api.environment_api import EnvironmentAPI
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.bastion_api import BastionAPI


# Uncomment next line to save error lines to /tmp/error.log
logger = get_logger()

aws_api = AWSAPI()


# pylint: disable= missing-function-docstring


@pytest.fixture(name="configuration")
def fixture_configuration():
    _configuration = EnvironmentAPIConfigurationPolicy()
    _configuration.project_name = "henvironment"
    _configuration.region = "il-central-1"
    _configuration.region = "us-west-2"
    _configuration.vpc_primary_subnet = "192.168.0.0/16"
    _configuration.tags = [{
            "Key": "Owner",
            "Value": "Horey"
        }]
    _configuration.vpc_name = "henvironment"
    _configuration.availability_zones_count = 3
    _configuration.subnet_mask_length = 24
    _configuration.subnet_name_template = "subnet-{type}-{id}"
    _configuration.route_table_name_template = "rt-{subnet}"
    _configuration.internet_gateway_name = f"igw-{_configuration.vpc_name}"
    _configuration.container_instance_security_group_name = f"sg_container_instance_{_configuration.vpc_name}"
    _configuration.secrets_manager_region = _configuration.region
    _configuration.container_instance_ssh_key_pair_name = f"container_instance_{_configuration.vpc_name}"
    _configuration.container_instance_launch_template_name = f"lt_container_instance_{_configuration.vpc_name}"
    _configuration.ecs_cluster_name = f"cluster_{_configuration.vpc_name}"
    _configuration.container_instance_role_name = f"role_container_instance_{_configuration.vpc_name}"
    _configuration.iam_path = f"/{_configuration.vpc_name}/"
    _configuration.container_instance_profile_name = f"instance_profile_container_instance_{_configuration.vpc_name}"
    _configuration.container_instance_auto_scaling_group_name = f"asg_container_instance_{_configuration.project_name}"
    _configuration.container_instance_auto_scaling_group_min_size = 1
    _configuration.container_instance_auto_scaling_group_max_size = 5
    _configuration.container_instance_capacity_provider_name = f"cp_ci_{_configuration.project_name}"
    _configuration.data_directory_path = Path(__file__).resolve().parent / "data"

    yield _configuration


@pytest.fixture(name="bastion_name")
def fixture_bastion_name(configuration):
    name = f"bastion_{configuration.project_name}"
    yield name


@pytest.mark.done
def test_provision_instance_profile(configuration, bastion_name):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    bastion = BastionAPI(env, bastion_name)
    assert bastion.provision_instance_profile()


@pytest.mark.done
def test_provision_ssh_key_pair(configuration, bastion_name):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    bastion = BastionAPI(env, bastion_name)
    assert bastion.provision_ssh_key_pair()


@pytest.mark.done
def test_provision_security_group(configuration, bastion_name):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    bastion = BastionAPI(env, bastion_name)
    assert bastion.provision_security_group()


@pytest.mark.done
def test_provision_instance(configuration, bastion_name):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    bastion = BastionAPI(env, bastion_name)
    profile = bastion.provision_instance_profile()
    ec2_instance = bastion.provision_instance(profile)
    assert ec2_instance.arn


@pytest.mark.done
def test_provision_ssh_config(configuration, bastion_name):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    bastion = BastionAPI(env, bastion_name)
    assert bastion.provision_ssh_config()


@pytest.mark.todo
def test_provision(configuration, bastion_name):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    bastion = BastionAPI(env, bastion_name)
    bastion.provision()


@pytest.mark.todo
def test_dispose(configuration, bastion_name):
    env = EnvironmentAPI(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    bastion = BastionAPI(env, bastion_name)
    bastion.dispose()
