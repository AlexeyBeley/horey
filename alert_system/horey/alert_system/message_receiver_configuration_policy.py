import datetime
import os

from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class MessageReceiverConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._slack_api_configuration_file = None
        self._deployment_datetime = None
        self._deployment_directory_path = None
        self._horey_repo_path = None

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

    @property
    def horey_repo_path(self):
        if self._horey_repo_path is None:
            raise RuntimeError()
        return self._horey_repo_path

    @horey_repo_path.setter
    def horey_repo_path(self, value):
        self._horey_repo_path = value

    @property
    def region(self):
        return "us-west-2"

    @property
    def sns_topic_name(self):
        return "alert_system_generic"

    @property
    def lambda_name(self):
        return "generic_receiver_test"

    @property
    def lambda_role_name(self):
        return "role-lambda-alert_system"

    @property
    def subscription_name(self):
        return "alert_system_generic_subscription"
