import datetime
import os

from horey.slack_api.slack_api_configuration_policy import SlackAPIConfigurationPolicy


class NotificationChannelSlackConfigurationPolicy(SlackAPIConfigurationPolicy):
    CONFIGURATION_FILE_NAME = "notification_channel_slack_configuration_values.py"

    def __init__(self):
        super().__init__()
        self._deployment_datetime = None

    @property
    def deployment_datetime(self):
        if self._deployment_datetime is None:
            self._deployment_datetime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
        return self._deployment_datetime
