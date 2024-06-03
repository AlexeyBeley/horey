"""
Alert system configuration policy.

"""

import datetime
import os
from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable=missing-function-docstring


class AlertSystemConfigurationPolicy(ConfigurationPolicy):
    """
    Main class.

    """

    def __init__(self):
        super().__init__()
        self._deployment_datetime = None
        self._deployment_directory_path = None
        self._horey_repo_path = None
        self._lambda_name = None
        self._sns_topic_name = None
        self._region = None
        self._notification_channels = None
        self._active_deployment_validation = False
        self._lambda_role_name = None
        self._lambda_role_path = None
        self._tags = None
        self._ses_configuration_set_name = None

    @property
    def deployment_datetime(self):
        if self._deployment_datetime is None:
            self._deployment_datetime = datetime.datetime.now().strftime(
                "%Y_%m_%d_%H_%M_%S"
            )
        return self._deployment_datetime

    @property
    def deployment_directory_path(self):
        if self._deployment_directory_path is None:
            self._deployment_directory_path = (
                f"/tmp/alert_system/{self.deployment_datetime}"
            )
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
            raise self.UndefinedValueError("horey_repo_path")
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
            raise ValueError("Lambda name was not set.")

        return self._lambda_name

    @lambda_name.setter
    def lambda_name(self, value):
        self._lambda_name = value

    @property
    def lambda_role_name(self):
        if self._lambda_role_name is None:
            self._lambda_role_name = "role-lambda-alert_system"
        return self._lambda_role_name

    @lambda_role_name.setter
    def lambda_role_name(self, value):
        self._lambda_role_name = value

    @property
    def lambda_role_path(self):
        if self._lambda_role_path is None:
            self._lambda_role_path = "role-lambda-alert_system"
        return self._lambda_role_path

    @lambda_role_path.setter
    def lambda_role_path(self, value):
        self._lambda_role_path = value

    @property
    def subscription_name(self):
        return "alert_system_generic_subscription"

    @property
    def lambda_timeout(self):
        return 30

    @property
    def notification_channels(self):
        return self._notification_channels

    @notification_channels.setter
    def notification_channels(self, value):
        self._notification_channels = value

    @property
    def active_deployment_validation(self):
        return self._active_deployment_validation

    @active_deployment_validation.setter
    def active_deployment_validation(self, value):
        self._active_deployment_validation = value

    @property
    def alert_system_lambda_log_group_name(self):
        return f"/aws/lambda/{self.lambda_name}"

    @property
    def self_monitoring_log_timeout_metric_name_raw(self):
        return f"{self.lambda_name}-log-timeout"

    @property
    def ses_configuration_set_name(self):
        if self._ses_configuration_set_name is None:
            self._ses_configuration_set_name = "conf_set_alert_system_default"

        return self._ses_configuration_set_name

    @ses_configuration_set_name.setter
    def ses_configuration_set_name(self, value):
        self._ses_configuration_set_name = value

    @property
    def tags(self):
        if self._tags is None:
            raise self.UndefinedValueError("tags")

        return self._tags

    @tags.setter
    def tags(self, value):
        self._tags = value
