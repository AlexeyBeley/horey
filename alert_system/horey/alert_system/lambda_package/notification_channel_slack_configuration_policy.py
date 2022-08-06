import datetime
import os

from horey.slack_api.slack_api_configuration_policy import SlackAPIConfigurationPolicy


class NotificationChannelSlackConfigurationPolicy(SlackAPIConfigurationPolicy):
    CONFIGURATION_FILE_NAME = "notification_channel_slack_configuration_values.py"

    def __init__(self):
        super().__init__()
        self._alert_system_monitoring_channel = None

    @property
    def alert_system_monitoring_channel(self):
        return self._alert_system_monitoring_channel

    @alert_system_monitoring_channel.setter
    def alert_system_monitoring_channel(self, value):
        self._alert_system_monitoring_channel = value
