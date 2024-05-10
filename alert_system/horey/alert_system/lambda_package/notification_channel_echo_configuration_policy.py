"""
Notification Channel to send SES emails.

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy
from horey.h_logger import get_logger

logger = get_logger()

# pylint: disable= missing-function-docstring


class NotificationChannelEchoConfigurationPolicy(ConfigurationPolicy):
    """
    Main class.

    """
