import datetime
import os

from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class MessageReceiverConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._slack_api_configuration_file = None
        self._deployment_datetime = None
        self._deployment_directory_path = None

    @property
    def slack_api_configuration_file(self):
        return self._slack_api_configuration_file

    @slack_api_configuration_file.setter
    def slack_api_configuration_file(self, value):
        self._slack_api_configuration_file = value

    @property
    def deployment_datetime(self):
        if self._deployment_datetime is None:
            self._deployment_datetime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
        return self._deployment_datetime

    @property
    def deployment_directory_path(self):
        if self._deployment_directory_path is None:
            self._deployment_directory_path = f"/tmp/alert_system/{self.deployment_datetime}"
        return self._deployment_directory_path

    @property
    def deployment_venv_path(self):
        return os.path.join(self.deployment_directory_path, "_venv")

    @property
    def lambda_zip_file_name(self):
        return "lambda_function.zip"
