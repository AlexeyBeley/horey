import datetime
import os

from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class AlertSystemConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._deployment_datetime = None
        self._deployment_directory_path = None
        self._horey_repo_path = None
        self._lambda_name = None
        self._sns_topic_name = None
        self._region = None

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
        if self._region is None:
            raise self.UndefinedValueError("region")

        return self._region

    @region.setter
    def region(self, value):
        self._region = value

    @property
    def sns_topic_name(self):
        if self._sns_topic_name is None:
            self._sns_topic_name = "alert_system_generic"
        return self._sns_topic_name

    @sns_topic_name.setter
    def sns_topic_name(self, value):
        self._sns_topic_name = value

    @property
    def lambda_name(self):
        if self._lambda_name is None:
            self._lambda_name = "generic_receiver_test"
        return self._lambda_name
    
    @lambda_name.setter
    def lambda_name(self, value):
        self._lambda_name = value 

    @property
    def lambda_role_name(self):
        return "role-lambda-alert_system"

    @property
    def subscription_name(self):
        return "alert_system_generic_subscription"

    @property
    def lambda_timeout(self):
        return 5
