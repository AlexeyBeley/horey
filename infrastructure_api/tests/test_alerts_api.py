"""
Init and cache AWS objects.

"""
import os.path

import pytest
from horey.aws_api.aws_api import AWSAPI
from horey.h_logger import get_logger
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.alerts_api_configuration_policy import AlertsAPIConfigurationPolicy
from pathlib import Path
# Uncomment next line to save error lines to /tmp/error.log
logger = get_logger()

aws_api = AWSAPI()


# pylint: disable= missing-function-docstring
configs_dir = Path(".").resolve().parent.parent.parent / "ignore" / "infrastructure_api"
real_life_env_configuration = str(configs_dir / "env_api_configs.json")
real_life_alerts_configuration = str(configs_dir / "alerts_api_configs.json")
assert os.path.exists(real_life_env_configuration)
assert os.path.exists(real_life_alerts_configuration)


@pytest.fixture(name="alerts_api")
def fixture_alerts_api():
    env_configuration = EnvironmentAPIConfigurationPolicy()
    env_configuration.configuration_file_full_path = real_life_env_configuration
    env_configuration.init_from_file()
    infrastructure_api = InfrastructureAPI()
    environment_api = infrastructure_api.get_environment_api(env_configuration, aws_api=aws_api)
    alerts_api_configuration = AlertsAPIConfigurationPolicy()
    alerts_api_configuration.configuration_file_full_path = real_life_alerts_configuration
    alerts_api_configuration.init_from_file()
    alerts_api = infrastructure_api.get_alerts_api(alerts_api_configuration, environment_api)
    yield alerts_api


@pytest.mark.done
def test_build_and_validate(alerts_api):
    ret = alerts_api.build_and_validate(None)
    assert ret
