"""
Init and cache AWS objects.

"""
import shutil
import sys
from pathlib import Path

import pytest


sys.path.append(str(Path(__file__).parent))
from test_utils import init_from_secrets_api

from horey.aws_api.aws_api import AWSAPI
from horey.common_utils.common_utils import CommonUtils
from horey.configuration_policy.configuration_policy import ConfigurationPolicy
from horey.h_logger import get_logger
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.secrets_api import SecretsAPI, SecretsAPIConfigurationPolicy


# pylint: disable= missing-function-docstring

mock_values_file_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_secrets_api_mocks.py"
mock_values = CommonUtils.load_module(mock_values_file_path)


logger = get_logger()

aws_api = AWSAPI()

class Configuration(ConfigurationPolicy):
    """
    Tests configuration
    """

    TEST_CONFIG = None

    def __init__(self):
        super().__init__()
        self._environment_api_configuration_file_secret_name = None

    @property
    def environment_api_configuration_file_secret_name(self):
        return self._environment_api_configuration_file_secret_name

    @environment_api_configuration_file_secret_name.setter
    def environment_api_configuration_file_secret_name(self, value: Path):
        self._environment_api_configuration_file_secret_name = value


@pytest.fixture(scope="session", autouse=True)
def setup_test_config():
    Configuration.TEST_CONFIG = init_from_secrets_api(Configuration, mock_values.secret_name)
    yield Configuration.TEST_CONFIG

@pytest.fixture(name="env_api_integration")
def fixture_env_api_integration():
    env_configuration = EnvironmentAPIConfigurationPolicy()
    env_configuration.data_directory_path = Path("/tmp/test_data")
    infrastructure_api = InfrastructureAPI()
    environment_api = infrastructure_api.get_environment_api(env_configuration, aws_api=aws_api)
    yield environment_api
    if env_configuration.data_directory_path.exists():
        shutil.rmtree(env_configuration.data_directory_path)


@pytest.fixture(name="secrets_api")
def fixture_secrets_api(env_api_integration):
    secrets_api_configuration = SecretsAPIConfigurationPolicy()
    secrets_api_configuration.region = "ca-central-1"
    yield SecretsAPI(secrets_api_configuration, env_api_integration)


@pytest.mark.unit
def test_get_secret(secrets_api):
    assert secrets_api.get_secret_file("test", Path("/tmp/test"))

