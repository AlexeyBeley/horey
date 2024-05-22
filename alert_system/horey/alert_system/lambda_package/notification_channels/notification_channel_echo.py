"""
Notification Channel to print log lines.

"""
from horey.alert_system.lambda_package.notification_channels.notification_channel_base import NotificationChannelBase
from horey.alert_system.lambda_package.notification import Notification

from horey.h_logger import get_logger

logger = get_logger()


class NotificationChannelEcho(NotificationChannelBase):
    """
    Main class.

    """

    def __init__(self, configuration):
        super().__init__(configuration)

    def notify(self, notification: Notification):
        """
        Send the notification to relevant channels.

        @param notification:
        @return:
        """

        if notification.type not in [notification_type.value for notification_type in Notification.Types]:
            notification.text = (
                f"Error in notification type. Auto set to CRITICAL: "
                f"received {str(notification.type)} must be one of {[notification_type.value for notification_type in Notification.Types]}.\n"
                f"Original message {notification.text}"
            )
            notification.type = Notification.Types.CRITICAL.value

        base_text = notification.text
        if not notification.tags:
            notification.tags = [self.configuration.ALERT_SYSTEM_MONITORING_ROUTING_TAG]
            notification.text = (
                    "Warning: Routing tags were not set. Using system monitoring.\n"
                    + base_text
            )

    def notify_alert_system_error(self, notification):
        """
        Alert system misconfiguration/malfunctioning alert

        :param notification:
        :return:
        """

        if notification.type == notification.Types.CRITICAL:
            logger.exception(notification.header, notification.text)
