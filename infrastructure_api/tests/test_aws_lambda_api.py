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
from horey.infrastructure_api.aws_lambda_api_configuration_policy import AWSLambdaAPIConfigurationPolicy


# pylint: disable= missing-function-docstring

mock_values_file_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_aws_lambda_api_mocks.py"
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
        self._stop_instance_ids = None

    @property
    def environment_api_configuration_file_secret_name(self):
        return self._environment_api_configuration_file_secret_name

    @environment_api_configuration_file_secret_name.setter
    def environment_api_configuration_file_secret_name(self, value: Path):
        self._environment_api_configuration_file_secret_name = value

    @property
    def stop_instance_ids(self):
        return self._stop_instance_ids

    @stop_instance_ids.setter
    def stop_instance_ids(self, value: Path):
        self._stop_instance_ids = value


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


@pytest.fixture(name="aws_lambda_api")
def fixture_aws_lambda_api(env_api_integration):
    infrastructure_api = InfrastructureAPI()
    aws_lambda_api_configuration = AWSLambdaAPIConfigurationPolicy()
    yield infrastructure_api.get_aws_lambda_api(aws_lambda_api_configuration, env_api_integration)


@pytest.mark.wip
def test_provision_instance_stopper_lambda(aws_lambda_api):
    aws_lambda_api.configuration.lambda_name = f"instance_stopper_{aws_lambda_api.environment_api.configuration.region}"
    aws_lambda_api.configuration.lambda_timeout = 30
    aws_lambda_api.configuration.lambda_memory_size = 1024
    aws_lambda_api.configuration.schedule_expression = "rate(1 minute)"
    aws_lambda_api.build_api.horey_git_api.configuration.git_directory_path = Path(__file__).parent.parent.parent.parent
    aws_lambda_api.build_api.horey_git_api.configuration.remote = "git@github.com:AlexeyBeley/horey.git"

    aws_lambda_api.environment_variables_callback = lambda: {"Variables": {"INSTANCE_IDS": Configuration.TEST_CONFIG.stop_instance_ids,
                                                                           "REGION": aws_lambda_api.environment_api.configuration.region}}

    def prepare_lambda_source_code_directory(branch_name):
        """
        Generate Dockerfile and horey repos.

        :param branch_name:
        :return:
        """

        horey_dir_preparator = aws_lambda_api.prepare_horey_lambda_source_code_directory(["aws_api"], "instance_stopper.handler")
        path = horey_dir_preparator(branch_name)

        shutil.copyfile(Path(__file__).parent / "aws_lambda_api_instance_stopper" / "instance_stopper.py", path)
        return path

    aws_lambda_api.build_api.prepare_source_code_directory = prepare_lambda_source_code_directory

    assert aws_lambda_api.provision_docker_lambda()
