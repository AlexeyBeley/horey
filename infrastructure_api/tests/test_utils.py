"""
Common test utilities for infrastructure_api tests.
"""
from typing import TypeVar
from pathlib import Path
import shutil

from horey.common_utils.common_utils import CommonUtils
from horey.configuration_policy.configuration_policy import ConfigurationPolicy
from horey.h_logger import get_logger
from horey.aws_api.aws_api import AWSAPI
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.secrets_api import SecretsAPI
from horey.infrastructure_api.secrets_api_configuration_policy import SecretsAPIConfigurationPolicy

mock_values_file_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_cicd_mocks.py"
mock_values = CommonUtils.load_module(mock_values_file_path)


logger = get_logger()


T = TypeVar('T', bound=ConfigurationPolicy)


def init_from_secrets_api(configuration_class: type[T], secret_name: str) -> T:
    """Download secret to temporary file and return file path."""
    env_configuration = EnvironmentAPIConfigurationPolicy()
    env_configuration.region = mock_values.region
    env_configuration.data_directory_path = Path("/tmp/test_data")

    aws_api = AWSAPI()
    infrastructure_api = InfrastructureAPI()
    environment_api = infrastructure_api.get_environment_api(env_configuration, aws_api=aws_api)


    secrets_api_configuration = SecretsAPIConfigurationPolicy()
    secrets_api_configuration.region = mock_values.region
    secrets_api = SecretsAPI(secrets_api_configuration, environment_api)
    file_path = secrets_api.get_secret_file(secret_name, env_configuration.data_directory_path)

    configuration = configuration_class()
    configuration.configuration_file_full_path = file_path
    configuration.init_from_file()
    if env_configuration.data_directory_path.exists():
        shutil.rmtree(env_configuration.data_directory_path)

    return configuration
