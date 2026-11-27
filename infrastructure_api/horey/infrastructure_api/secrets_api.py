"""
Standard.

"""
from pathlib import Path

from horey.aws_api.base_entities.region import Region
from horey.h_logger import get_logger
from horey.infrastructure_api.secrets_api_configuration_policy import SecretsAPIConfigurationPolicy

from horey.infrastructure_api.environment_api import EnvironmentAPI

logger = get_logger()


class SecretsAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration: SecretsAPIConfigurationPolicy, environment_api: EnvironmentAPI):
        self.configuration = configuration
        self.environment_api = environment_api

    @property
    def region(self):
        try:
            return Region.get_region(self.configuration.region)
        except self.configuration.UndefinedValueError:
            return self.environment_api.region

    def get_secret_file(self, secret_name: str, file_path: Path):
        """
        Get secret file from AWS Secrets Manager

        :param secret_name:
        :param file_path:
        :return:
        """

        logger.info(f"Downloading secret {secret_name} to {file_path}")
        return self.environment_api.aws_api.get_secret_file(secret_name, file_path, region=self.region)

    def get_secret(self, secret_name: str, ignore_missing=False):
        """
        Get secret string from AWS Secrets Manager

        :param ignore_missing:
        :param secret_name:
        :return:
        """

        logger.info(f"Downloading secret {secret_name}")
        return self.environment_api.aws_api.get_secret_value(secret_name, region=self.region, ignore_missing=ignore_missing)

