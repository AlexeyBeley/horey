"""
Notification channel base class
"""


class NotificationChannelBase:
    """
    This class is a base class for all notification channels implementations.

    """

    NOTIFICATION_CHANNELS_ENVIRONMENT_VARIABLE = "ALERT_SYSTEM_NOTIFICATION_CHANNELS"

    def __init__(self, configuration):
        self.configuration = configuration
