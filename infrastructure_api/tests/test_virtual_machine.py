"""
Init and cache AWS objects.

"""
from pathlib import Path

import pytest
from horey.aws_api.aws_api import AWSAPI
from horey.h_logger import get_logger
from horey.infrastructure_api.environment_api import EnvironmentAPI
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.virtual_machine_api import VirtualMachineAPI
from horey.infrastructure_api.virtual_machine_api_configuration_policy import VirtualMachineAPIConfigurationPolicy


# Uncomment next line to save error lines to /tmp/error.log
logger = get_logger()

# pylint: disable= missing-function-docstring

config_dir_path = (Path(__file__).resolve().parent.parent.parent.parent / "ignore"/ "infrastructure_api").absolute()

env_config_file_path = config_dir_path / "environment_x"
api_config_file_path = config_dir_path / "virtual_machine_api_configuration_x"


@pytest.fixture(name="environment_configuration_test")
def fixture_configuration():
    _configuration = EnvironmentAPIConfigurationPolicy()
    _configuration.project_name = "henvironment"
    _configuration.region = "il-central-1"
    _configuration.vpc_primary_subnet = "192.168.0.0/16"
    _configuration.tags = [{
            "Key": "Owner",
            "Value": "Horey"
        }]
    _configuration.vpc_name = "henvironment"
    _configuration.subnet_mask_length = 24

    yield _configuration


@pytest.fixture(name="environment_api")
def fixture_configuration():
    _configuration = EnvironmentAPIConfigurationPolicy()
    _configuration.configuration_file_full_path = env_config_file_path
    _configuration.init_from_file()

    aws_api = AWSAPI()
    yield EnvironmentAPI(_configuration, aws_api)


@pytest.fixture(name="api")
def fixture_configuration():
    _configuration = EnvironmentAPIConfigurationPolicy()
    _configuration.configuration_file_full_path = env_config_file_path
    _configuration.init_from_file()

    aws_api = AWSAPI()
    environment_api = EnvironmentAPI(_configuration, aws_api)

    api_configuration = VirtualMachineAPIConfigurationPolicy()
    api_configuration.configuration_file_full_path = api_config_file_path
    api_configuration.init_from_file()
    yield VirtualMachineAPI(api_configuration, environment_api)


@pytest.mark.unit
def test_get_ubuntu24_image(api):
    assert api.get_ubuntu24_image()


@pytest.mark.unit
def test_provision(api):
    assert api.provision_instance_profile()


@pytest.mark.unit
def test_provision_ssh_key_pair(api):
    assert api.provision_ssh_key_pair()


@pytest.mark.unit
def test_provision_security_group(api):
    assert api.provision_security_group()


@pytest.mark.unit
def test_provision_instance(api):
    assert api.provision_instance()
