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
from horey.infrastructure_api.s3_api_configuration_policy import S3APIConfigurationPolicy
from horey.infrastructure_api.aws_lambda_api_configuration_policy import AWSLambdaAPIConfigurationPolicy
from horey.aws_api.aws_services_entities.s3_bucket import S3Bucket


# pylint: disable= missing-function-docstring

mock_values_file_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_s3_api_mocks.py"
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
        self._event_configuration_bucket_name = None
        self._event_configuration_lambda_name = None
        self._environment_api_configuration_file_secret_name = None

    @property
    def environment_api_configuration_file_secret_name(self):
        return self._environment_api_configuration_file_secret_name

    @environment_api_configuration_file_secret_name.setter
    def environment_api_configuration_file_secret_name(self, value: Path):
        self._environment_api_configuration_file_secret_name = value

    @property
    def event_configuration_lambda_name(self):
        return self._event_configuration_lambda_name

    @event_configuration_lambda_name.setter
    def event_configuration_lambda_name(self, value: Path):
        self._event_configuration_lambda_name = value

    @property
    def event_configuration_bucket_name(self):
        return self._event_configuration_bucket_name

    @event_configuration_bucket_name.setter
    def event_configuration_bucket_name(self, value: Path):
        self._event_configuration_bucket_name = value

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


@pytest.fixture(name="s3_api")
def fixture_s3_api(env_api_integration):
    infrastructure_api = InfrastructureAPI()
    s3_api_configuration = S3APIConfigurationPolicy()
    yield infrastructure_api.get_s3_api(s3_api_configuration, env_api_integration)

@pytest.fixture(name="lambda_api")
def fixture_lambda_api(env_api_integration):
    infrastructure_api = InfrastructureAPI()
    lambda_api_configuration = AWSLambdaAPIConfigurationPolicy()
    yield infrastructure_api.get_aws_lambda_api(lambda_api_configuration, env_api_integration)



@pytest.mark.skip(reason = "not checked")
def test_provision_glue_database(s3_api):
    db_test  = s3_api.provision_bucket("test")
    assert db_test


@pytest.mark.unit
def test_provision_bucket_notification_configuration_lambda(s3_api, lambda_api):
    bucket = S3Bucket({"Name": Configuration.TEST_CONFIG.event_configuration_bucket_name})

    statement = lambda_api.generate_s3_trigger_statement(bucket)
    lambda_api.configuration.policy["Statement"].append(statement)
    aws_lambda = lambda_api.provision_echo_lambda()

    config = s3_api.provision_bucket_notification_configuration_lambda(bucket, aws_lambda)
    assert config

@pytest.mark.unit
def test_add_bucket_notification_configuration_lambda(s3_api, lambda_api):
    bucket = S3Bucket({"Name": Configuration.TEST_CONFIG.event_configuration_bucket_name})

    statement = lambda_api.generate_s3_trigger_statement(bucket)
    lambda_api.configuration.policy["Statement"].append(statement)
    aws_lambda = lambda_api.provision_echo_lambda()

    config = s3_api.add_bucket_notification_configuration_lambda(bucket, aws_lambda)
    assert config
