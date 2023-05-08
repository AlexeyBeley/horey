"""
Configs
"""
from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring


class HumanAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class
    """
    def __init__(self):
        self._azure_devops_api_configuration_file_path = None
        super().__init__()

    @property
    def azure_devops_api_configuration_file_path(self):
        if self._azure_devops_api_configuration_file_path is None:
            raise ValueError("azure_devops_api_configuration_file_path was not set")
        return self._azure_devops_api_configuration_file_path

    @azure_devops_api_configuration_file_path.setter
    def azure_devops_api_configuration_file_path(self, value):
        """
        http://127.0.0.1:8888
        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(
                f"azure_devops_api_configuration_file_path must be string received {value} of type: {type(value)}"
            )

        self._azure_devops_api_configuration_file_path = value
