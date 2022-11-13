import datetime
import os

from horey.slack_api.slack_api_configuration_policy import SlackAPIConfigurationPolicy


class NotificationChannelSlackConfigurationPolicy(SlackAPIConfigurationPolicy):
    CONFIGURATION_FILE_NAME = "notification_channel_slack_configuration_values.py"
    ALERT_SYSTEM_MONITORING_ROUTING_TAG = "alert_system_monitoring"

    def __init__(self):
        super().__init__()
        self._alert_system_monitoring_destination = None
        self._tag_to_channel_mapping = None

    @property
    def alert_system_monitoring_destination(self):
        return self.tag_to_channel_mapping.get(self.ALERT_SYSTEM_MONITORING_ROUTING_TAG)

    @alert_system_monitoring_destination.setter
    def alert_system_monitoring_destination(self, value):
        if not isinstance(value, str):
            raise ValueError(value)

        self._alert_system_monitoring_destination = value

    @property
    def tag_to_channel_mapping(self):
        return self._tag_to_channel_mapping

    @tag_to_channel_mapping.setter
    def tag_to_channel_mapping(self, value):
        if not isinstance(value, dict):
            raise ValueError(value)

        if not isinstance(value.get(self.ALERT_SYSTEM_MONITORING_ROUTING_TAG), str):
            raise ValueError(
                f"Key {self.ALERT_SYSTEM_MONITORING_ROUTING_TAG} is incorrect in mappings: {value}"
            )
        self._tag_to_channel_mapping = value
