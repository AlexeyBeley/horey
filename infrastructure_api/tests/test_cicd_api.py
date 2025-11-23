"""
Init and cache AWS objects.

"""
import os.path

import pytest
from horey.aws_api.aws_api import AWSAPI
from horey.h_logger import get_logger
from horey.infrastructure_api.cicd_api import CICDAPIConfigurationPolicy, CICDAPI
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.ecs_api_configuration_policy import ECSAPIConfigurationPolicy
from pathlib import Path
# Uncomment next line to save error lines to /tmp/error.log
logger = get_logger()

aws_api = AWSAPI()


# pylint: disable= missing-function-docstring
configs_dir = Path(".").resolve().parent.parent.parent / "ignore" / "infrastructure_api"
real_life_env_configuration = str(configs_dir / "env_api_configs.json")
real_life_configuration = str(configs_dir / "cicd_api_configs.json")
assert os.path.exists(real_life_env_configuration)
assert os.path.exists(real_life_configuration)


@pytest.fixture(name="cicd_api")
def fixture_cicd_api():
    env_configuration = EnvironmentAPIConfigurationPolicy()
    env_configuration.configuration_file_full_path = real_life_env_configuration
    env_configuration.init_from_file()
    infrastructure_api = InfrastructureAPI()
    environment_api = infrastructure_api.get_environment_api(env_configuration, aws_api=aws_api)
    cicd_api_configuration = CICDAPIConfigurationPolicy()
    cicd_api_configuration.configuration_file_full_path = real_life_configuration
    cicd_api_configuration.init_from_file()
    cicd_api = infrastructure_api.get_cicd_api(cicd_api_configuration, environment_api)
    yield cicd_api


@pytest.mark.wip
def test_provision_ecs_task_definition(cicd_api):
    # use existing image
    step = cicd_api.generate_provision_constructor_bootstrap_step(Path("remote_deployment_dir_path"))
