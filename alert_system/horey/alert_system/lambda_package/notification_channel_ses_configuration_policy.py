"""
Notification Channel to send SES emails.

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy
from horey.h_logger import get_logger

logger = get_logger()

# pylint: disable= missing-function-docstring


class NotificationChannelSESConfigurationPolicy(ConfigurationPolicy):
    """
    Main class.

    """
    def __init__(self):
        super().__init__()
        self._region = None
        self._src_email = None
        self._routing_tag_to_email_mapping = None
        self._alert_system_monitoring_destination = None

    @property
    def alert_system_monitoring_destination(self):
        return self._alert_system_monitoring_destination

    @alert_system_monitoring_destination.setter
    def alert_system_monitoring_destination(self, value):
        self._alert_system_monitoring_destination = value

    @property
    def routing_tag_to_email_mapping(self):
        return self._routing_tag_to_email_mapping

    @routing_tag_to_email_mapping.setter
    def routing_tag_to_email_mapping(self, value):
        self._routing_tag_to_email_mapping = value

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, value):
        self._region = value

    @property
    def src_email(self):
        return self._src_email

    @src_email.setter
    def src_email(self, value):
        self._src_email = value
