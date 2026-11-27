"""
Standard qa maintainer.

"""
from pathlib import Path

from horey.aws_api.base_entities.region import Region
from horey.infrastructure_api.qa_api_configuration_policy import QAAPIConfigurationPolicy
from horey.infrastructure_api.environment_api import EnvironmentAPI, EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.secrets_api import SecretsAPI, SecretsAPIConfigurationPolicy
from horey.h_logger import get_logger
from horey.aws_api.aws_api import AWSAPI


logger = get_logger()


class QAAPI:
    """
    Manage testing.

    """

    def __init__(self, configuration: QAAPIConfigurationPolicy, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api
     
    @staticmethod
    def init_from_configuration(configuration_class: type[T]):
        config_file_path = configuration_class().configuration_file_full_path
        configuration = configuration_class()
        configuration.init_from_file(config_file_path)

        env_configuration = EnvironmentAPIConfigurationPolicy()
        env_configuration.region = configuration.secrets_region
        environment_api = EnvironmentAPI(env_configuration, aws_api=AWSAPI())
        qa_api_configuration = QAAPIConfigurationPolicy()
        return QAAPI(qa_api_configuration, environment_api)

    @staticmethod
    def setup_test_config(configuration: type[T]):
        qa_api = QAAPI.init_from_configuration(configuration) 
        configuration.TEST_CONFIG = qa_api.init_from_secrets_api(configuration)
        configuration.QA_API = qa_api
        return configuration 
    
    def init_from_secrets_api(self, configuration_class: type[T]) -> T:
        """
        Download secret to temporary file and return file path.
        """

        base_config_file_path = configuration_class().configuration_file_full_path
        base_configuration = configuration_class()
        base_configuration.init_from_file(base_config_file_path)
        
        secrets_api_configuration = SecretsAPIConfigurationPolicy()
        secrets_api = SecretsAPI(secrets_api_configuration, self.environment_api)
        file_path = secrets_api.get_secret_file(base_configuration.secret_name, self.configuration.tests_data_directory_path)

        configuration = configuration_class()
        configuration.configuration_file_full_path = file_path
        if not configuration.init_from_file():
            raise RuntimeError("Was not able to init")
        
        for key in dir(configuration):
            if key.startswith("secret_file"):
                secrets_api.get_secret_file(getattr(configuration, key), self.configuration.tests_data_directory_path)
        return configuration
