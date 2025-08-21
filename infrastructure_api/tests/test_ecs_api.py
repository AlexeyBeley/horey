"""
Init and cache AWS objects.

"""
import os.path

import pytest
from horey.aws_api.aws_api import AWSAPI
from horey.h_logger import get_logger
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
real_life_alerts_configuration = str(configs_dir / "ecs_api_configs.json")
assert os.path.exists(real_life_env_configuration)
assert os.path.exists(real_life_alerts_configuration)


@pytest.fixture(name="service_api")
def fixture_ecs_api():
    env_configuration = EnvironmentAPIConfigurationPolicy()
    env_configuration.configuration_file_full_path = real_life_env_configuration
    env_configuration.init_from_file()
    infrastructure_api = InfrastructureAPI()
    environment_api = infrastructure_api.get_environment_api(env_configuration, aws_api=aws_api)
    service_api_configuration = ECSAPIConfigurationPolicy()
    service_api_configuration.configuration_file_full_path = real_life_alerts_configuration
    service_api_configuration.init_from_file()
    service_api = infrastructure_api.get_ecs_api(service_api_configuration, environment_api)
    yield service_api


@pytest.mark.unit
def test_provision_ecs_task_definition(service_api):
    # use existing image
    ecr_image_tag = service_api.get_build_tag()
    service_api.environment_variables_callback = lambda : [{
                "name": f"NAME{i}",
                "value": "Value"*120
            } for i in range(1000)]
    with pytest.raises(ValueError, match=r".*Task definition request length.*"):
        service_api.provision_ecs_task_definition(ecr_image_tag)
