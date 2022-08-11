"""
Notification channel base class
"""
from notification import Notification


class NotificationChannelBase:
    """
    This class is a base class for all notification channels implementations.

    """

    NOTIFICATION_CHANNELS_ENVIRONMENT_VARIABLE = "ALERT_SYSTEM_NOTIFICATION_CHANNELS"

    def __init__(self, configuration):
        self.configuration = configuration

    def notify(self, notification: Notification):
        """
        Send the notification to all the destination relevant to its tag.

        @param notification:
        @return:
        """

        raise NotImplementedError("notify not implemented.")

    def notify_alert_system_error(self, notification: Notification):
        """
        Notify self monitoring problem.

        @param notification:
        @return:
        """
        raise NotImplementedError("notify_alert_system_error not implemented.")

    class UnknownTag(ValueError):
        """
        Raise in case tag specified has no route.
        """
