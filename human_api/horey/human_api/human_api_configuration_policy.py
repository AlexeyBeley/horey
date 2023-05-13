"""
Configs
"""
import datetime
import os

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring


class HumanAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class
    """
    def __init__(self):
        self._azure_devops_api_configuration_file_path = None
        self._reports_dir_path = None
        self._sprint_name = None
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

    @property
    def daily_hapi_file_path(self):
        return os.path.join(self.daily_dir_path, "daily.hapi")

    @property
    def protected_input_file_path(self):
        return os.path.join(self.daily_dir_path, "daily_input.hapi")

    @property
    def output_file_path(self):
        return os.path.join(self.daily_dir_path, "daily_output.hapi")

    @property
    def daily_dir_path(self):
        return os.path.join(self.reports_dir_path, str(datetime.date.today()))

    @property
    def reports_dir_path(self):
        if self._reports_dir_path is None:
            raise self.UndefinedValueError("reports_dir_path")
        return self._reports_dir_path

    @reports_dir_path.setter
    def reports_dir_path(self, value):
        self._reports_dir_path = value
    
    @property
    def sprint_name(self):
        if self._sprint_name is None:
            raise self.UndefinedValueError("sprint_name")
        return self._sprint_name

    @sprint_name.setter
    def sprint_name(self, value):
        self._sprint_name = value
