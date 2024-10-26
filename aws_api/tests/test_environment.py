"""
Init and cache AWS objects.

"""

import os
import json

import pytest
from horey.aws_api.aws_api import AWSAPI
from horey.h_logger import get_logger
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.aws_api.base_entities.region import Region
from horey.aws_api.solutions.environment import Environment
from horey.aws_api.solutions.environment_configuration_policy import EnvironmentConfigurationPolicy


# Uncomment next line to save error lines to /tmp/error.log
logger = get_logger()

aws_api_configuration = AWSAPIConfigurationPolicy()
aws_api_configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "..",
        "ignore",
        "aws_api_configuration_values.py",
    )
)

aws_api_configuration.init_from_file()
aws_api = AWSAPI(configuration=aws_api_configuration)


# pylint: disable= missing-function-docstring


@pytest.fixture(name="configuration")
def fixture_configuration():
    _configuration = EnvironmentConfigurationPolicy()
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
    yield _configuration


@pytest.mark.done
def test_init_environment(configuration):
    assert Environment(configuration, aws_api)


@pytest.mark.wip
def test_provision_vpc(configuration):
    env = Environment(configuration, aws_api)
    env.provision_vpc()


@pytest.mark.wip
def test_provision_subnets(configuration):
    env = Environment(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    env.provision_subnets()


@pytest.mark.wip
def test_provision_internet_gateway(configuration):
    env = Environment(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    inet_gwy = env.provision_internet_gateway()
    assert inet_gwy.id


@pytest.mark.wip
def test_provision_public_route_tables(configuration):
    env = Environment(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    inet_gwy = env.provision_internet_gateway()
    route_tables = env.provision_public_route_tables(inet_gwy)
    assert route_tables


@pytest.mark.done
def test_dispose_subnets(configuration):
    env = Environment(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    env.dispose_subnets()


@pytest.mark.done
def test_dispose_route_tables(configuration):
    env = Environment(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    assert env.dispose_route_tables()


@pytest.mark.done
def test_dispose_internet_gateway(configuration):
    env = Environment(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    assert env.dispose_internet_gateway()


@pytest.mark.done
def test_dispose_vpc(configuration):
    env = Environment(configuration, aws_api)
    env.aws_api.ec2_client.clear_cache(None, all_cache=True)
    env.dispose_vpc()