"""
Init and cache AWS objects.

"""

from pathlib import Path
import pytest
from horey.aws_api.aws_api import AWSAPI
from horey.h_logger import get_logger
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.build_api import BuildAPI, BuildAPIConfigurationPolicy
from horey.infrastructure_api.qa_api import QAAPI, QAAPIConfigurationPolicy
from horey.configuration_policy.configuration_policy import ConfigurationPolicy
logger = get_logger()

aws_api = AWSAPI()



# pylint: disable= missing-function-docstring

class Configuration(ConfigurationPolicy):
    TEST_CONFIG = None
    QA_API = None

    def __init__(self):
        super().__init__()
        self.configuration_file_full_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_build_api_mocks.py"
        self._secret_file_github_api_configuration_file_name = None
        self._github_action_name = None
        self._github_repo_name = None
        self._secrets_region = None
        self._secret_name = None

        self._branch_name = None

    @property
    def branch_name(self):
        return self._branch_name

    @branch_name.setter
    def branch_name(self, value):
        self._branch_name = value

    @property
    def secret_name(self):
        return self._secret_name

    @secret_name.setter
    def secret_name(self, value):
        self._secret_name = value

    @property
    def secrets_region(self):
        return self._secrets_region

    @secrets_region.setter
    def secrets_region(self, value):
        self._secrets_region = value

    @property
    def github_repo_name(self):
        return self._github_repo_name

    @github_repo_name.setter
    def github_repo_name(self, value):
        self._github_repo_name = value

    @property
    def github_action_name(self):
        return self._github_action_name

    @github_action_name.setter
    def github_action_name(self, value):
        self._github_action_name = value

    @property
    def secret_file_github_api_configuration_file_name(self):
        return self._secret_file_github_api_configuration_file_name

    @secret_file_github_api_configuration_file_name.setter
    def secret_file_github_api_configuration_file_name(self, value):
        self._secret_file_github_api_configuration_file_name = value


@pytest.fixture(scope="session", autouse=True)
def setup_test_config():
    QAAPI.setup_test_config(Configuration)
    yield Configuration.TEST_CONFIG


@pytest.fixture(name="build_api")
def fixture_build_api():
    env_configuration = EnvironmentAPIConfigurationPolicy()
    env_configuration.project_name = "hry"
    env_configuration.project_name_abbr = "hry"
    env_configuration.environment_level = "development"
    env_configuration.environment_name = "test"
    env_configuration.region = "us-west-2"
    infrastructure_api = InfrastructureAPI()
    environment_api = infrastructure_api.get_environment_api(env_configuration, aws_api=aws_api)
    build_api_configuration = BuildAPIConfigurationPolicy()
    build_api = BuildAPI(build_api_configuration, environment_api)
    yield build_api


class Mocker:
    BUILD_COUNTER = 0

    # pylint: disable= unused-argument
    @staticmethod
    def build_mock(dir, tags, nocache=None, **kwargs):
        """
        Raises.

        :param dir:
        :param tags:
        :param nocache:
        :param kwargs:
        :return:
        """

        if Mocker.BUILD_COUNTER == 1:
            return True
        Mocker.BUILD_COUNTER = 1

        raise RuntimeError("authorization token has expired")


@pytest.mark.unit
def test_build_docker_image(build_api):
    build_api.docker_build_directory.mkdir(exist_ok=True)
    build_api.add_ecr_registry_credentials()
    with open(build_api.docker_build_directory / "Dockerfile", "w", encoding="utf-8") as file_handler:
        file_handler.write(f"FROM {build_api.environment_api.aws_api.ec2_client.account_id}.dkr.ecr.{build_api.environment_api.configuration.region}.amazonaws.com/horey:0")
    build_api.environment_api.docker_api.build = Mocker.build_mock
    ret = build_api.build_docker_image(build_api.docker_build_directory, ["sub_tag0,sub_tag1"])

    assert ret


@pytest.mark.unit
def test_get_ecr_registry_credentials(build_api):
    ret = build_api.get_ecr_registry_credentials()
    assert len(ret) == 3

@pytest.mark.unit
def test_trigger_github_action(build_api):
    assert build_api.trigger_github_action(Configuration.QA_API.configuration.tests_data_directory_path/Configuration.TEST_CONFIG.secret_file_github_api_configuration_file_name, Configuration.TEST_CONFIG.github_repo_name, Configuration.TEST_CONFIG.github_action_name, Configuration.TEST_CONFIG.branch_name)
