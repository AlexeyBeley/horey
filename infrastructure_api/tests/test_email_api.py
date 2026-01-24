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
from horey.infrastructure_api.email_api_configuration_policy import EmailAPIConfigurationPolicy

# pylint: disable= missing-function-docstring


mock_values_file_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_email_api_mocks.py"
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
    env_configuration = init_from_secrets_api(EnvironmentAPIConfigurationPolicy, Configuration.TEST_CONFIG.environment_api_configuration_file_secret_name)
    env_configuration.data_directory_path = Path("/tmp/test_data")
    infrastructure_api = InfrastructureAPI()
    environment_api = infrastructure_api.get_environment_api(env_configuration, aws_api=aws_api)
    yield environment_api
    if env_configuration.data_directory_path.exists():
        shutil.rmtree(env_configuration.data_directory_path)


@pytest.fixture(name="email_api")
def fixture_email_api(env_api_integration):
    infrastructure_api = InfrastructureAPI()
    email_api_configuration = EmailAPIConfigurationPolicy()
    email_api = infrastructure_api.get_email_api(email_api_configuration, env_api_integration)
    yield email_api


@pytest.mark.unit
def test_init_environment(email_api):
    ret = email_api.send_email("test.horey@horey.com")
    assert ret


@pytest.mark.unit
def test_get_suppressed_emails(email_api):
    ret = email_api.get_suppressed_emails()
    assert ret


@pytest.mark.unit
def test_unsupress_email(email_api):
    email_addr = "horey@horey.com"
    ret = email_api.unsupress_email(email_addr)
    assert ret


@pytest.mark.unit
def test_grep_suppressed_emails(email_api):
    ret = email_api.grep_suppressed_emails("horey")
    for x in ret:
        print(x)
    assert ret
