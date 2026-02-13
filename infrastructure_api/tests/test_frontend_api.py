"""
Init and cache AWS objects.

"""
import json
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
from horey.infrastructure_api.frontend_api_configuration_policy import FrontendAPIConfigurationPolicy
# Uncomment next line to save error lines to /tmp/error.log


# pylint: disable= missing-function-docstring

mock_values_file_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_frontend_api_mocks.py"
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
        self._s3_bucket_name = None
        self._s3_bucket_path = None
        self._environment_api_configuration_file_secret_name = None
        self._dns_address = None

    @property
    def environment_api_configuration_file_secret_name(self):
        return self._environment_api_configuration_file_secret_name

    @environment_api_configuration_file_secret_name.setter
    def environment_api_configuration_file_secret_name(self, value: Path):
        self._environment_api_configuration_file_secret_name = value

    @property
    def s3_bucket_name(self):
        return self._s3_bucket_name

    @s3_bucket_name.setter
    def s3_bucket_name(self, value):
        self._s3_bucket_name = value

    @property
    def s3_bucket_path(self):
        return self._s3_bucket_path

    @s3_bucket_path.setter
    def s3_bucket_path(self, value):
        self._s3_bucket_path = value

    @property
    def dns_address(self):
        return self._dns_address

    @dns_address.setter
    def dns_address(self, value):
        self._dns_address = value


@pytest.fixture(scope="session", autouse=True)
def setup_test_config():
    Configuration.TEST_CONFIG = init_from_secrets_api(Configuration, mock_values.secret_name)
    yield Configuration.TEST_CONFIG

@pytest.fixture(name="env_api_integration")
def fixture_env_api_integration():
    env_configuration = init_from_secrets_api(EnvironmentAPIConfigurationPolicy, Configuration.TEST_CONFIG.environment_api_configuration_file_secret_name)
    env_configuration.data_directory_path = Path("/tmp/test_data")
    infrastructure_api = InfrastructureAPI()
    environment_api = infrastructure_api.get_environment_api(env_configuration, aws_api=aws_api)
    yield environment_api
    if env_configuration.data_directory_path.exists():
        shutil.rmtree(env_configuration.data_directory_path)


@pytest.fixture(name="frontend_api")
def fixture_frontend_api(env_api_integration):
    infrastructure_api = InfrastructureAPI()
    frontend_api_configuration = FrontendAPIConfigurationPolicy()
    yield infrastructure_api.get_frontend_api(frontend_api_configuration, env_api_integration)

@pytest.mark.wip
def test_provision_cloudfront(frontend_api):
    assert frontend_api.provision_cloudfront(Configuration.TEST_CONFIG.s3_bucket_name,
                                             Configuration.TEST_CONFIG.s3_bucket_path,
                                             Configuration.TEST_CONFIG.dns_address)
