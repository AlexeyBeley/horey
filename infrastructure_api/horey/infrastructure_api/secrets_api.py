"""
Standard.

"""

from horey.h_logger import get_logger
from horey.infrastructure_api.secrets_api_configuration_policy import SecretsAPIConfigurationPolicy

logger = get_logger()


class SecretsAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration:SecretsAPIConfigurationPolicy, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api

