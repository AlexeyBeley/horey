"""
Notification Channel to print log lines.
This module is both main class holder and notification channel initializer

"""
from horey.alert_system.lambda_package.notification import Notification
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy

from horey.h_logger import get_logger

logger = get_logger()


class NotificationChannelEcho:
    """
    Main class.

    """

    def notify(self, notification: Notification):
        """
        Send the notification to relevant channels.

        @param notification:
        @return:
        """

        if notification.type not in Notification.Types:
            notification.text = (
                f"Error in notification type. Auto set to CRITICAL: "
                f"received {str(notification.type)} must be one of {Notification.Types}.\n"
                f"Original message {notification.text}"
            )
            notification.type = Notification.Types.CRITICAL

        base_text = notification.text
        if not notification.routing_tags:
            notification.routing_tags = [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG]
            notification.text = (
                    "Warning: Routing tags were not set. Using system monitoring.\n"
                    + base_text
            )
        try:
            line = f"{notification.header=}, {notification.text=}, {notification.routing_tags=}"
        except Exception as error_inst:
            line = f"Error formatting log line: {repr(error_inst)}"

        line = line.replace(AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_LOG_ERROR_FILTER_PATTERN,
                            "ALERT_SYSTEM_SELF_MONITORING_LOG_ERROR_FILTER_PATTERN")
        line = line.replace(AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_LOG_TIMEOUT_FILTER_PATTERN,
                            "ALERT_SYSTEM_SELF_MONITORING_LOG_TIMEOUT_FILTER_PATTERN")

        if notification.type in [Notification.Types.CRITICAL, Notification.Types.WARNING]:
            logger.warning(line)
        else:
            logger.info(line)
        return True

    @staticmethod
    def notify_alert_system_error(notification):
        """
        Alert system misconfiguration/malfunctioning alert

        :param notification:
        :return:
        """

        line = f"{notification.header=}, {notification.text=}, {notification.routing_tags=}"
        logger.exception(line)
        return True


def main():
    """
    This module is initializer by itself.

    :return:
    """

    return NotificationChannelEcho()
