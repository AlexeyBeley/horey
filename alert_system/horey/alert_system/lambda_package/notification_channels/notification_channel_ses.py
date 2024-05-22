"""
Notification Channel to send SES email.

"""

import traceback

from notification_channel_base import NotificationChannelBase
from notification import Notification

from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.base_entities.region import Region
from horey.h_logger import get_logger

logger = get_logger()


class NotificationChannelSES(NotificationChannelBase):
    """
    Main class.

    """

    def __init__(self, configuration):
        super().__init__(configuration)
        self.aws_api = AWSAPI(configuration=None)

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

        for routing_tag in notification.tags:
            try:
                dst_emails = self.map_routing_tag_to_destinations(routing_tag)
            except self.UnknownTagError:
                dst_emails = self.map_routing_tag_to_destinations(
                    self.configuration.ALERT_SYSTEM_MONITORING_ROUTING_TAG
                )
                notification.text = (
                        f"!!!WARNING!!!:\n Routing tag '{routing_tag}' has no mapping.\n"
                        f" Using system monitoring routing tag.\n\n" + base_text
                )

            self.send_email(notification, dst_emails)

    def map_routing_tag_to_destinations(self, tag):
        """
        Find matching channels to this routing tag.

        @param tag:
        @return:
        """

        routes = self.configuration.routing_tag_to_email_mapping.get(tag)
        if routes is None:
            raise self.UnknownTagError(tag)

        if isinstance(routes, str):
            routes = [routes]

        return routes

    def notify_alert_system_error(self, notification: Notification):
        """
        Notify self monitoring problem.

        @param notification:
        @return:
        """

        dict_req = self.generate_ses_request(notification, [self.configuration.alert_system_monitoring_destination])
        self.send_email_raw(dict_req)

    def generate_ses_request(self, notification, dst_emails):
        """

        :param notification:
        :return:
        """
        dict_req = {"FromEmailAddress": self.configuration.src_email,
                    "Destination": {"ToAddresses": dst_emails},
                    "Content": {"Simple": {
                        "Subject": {
                            "Data": notification.header,
                            "Charset": "UTF-8"
                        },
                        "Body": {
                            "Text": {
                                "Data": notification.text,
                                "Charset": "UTF-8"
                            }
                        },
                        "Headers": [
                            {
                                "Name": "header-name",
                                "Value": "header-value"
                            },
                        ]
                    }}}
        return dict_req

    def send_email(self, notification, dst_emails):
        """
        Send email.

        :param notification:
        :return:
        """
        logger.info("Sending message to slack")
        try:
            dict_req = self.generate_ses_request(notification, dst_emails)
            self.send_email_raw(dict_req)
        except Exception as exception_inst:
            traceback_str = "".join(traceback.format_tb(exception_inst.__traceback__))
            logger.exception(traceback_str)

            notification = Notification()
            notification.type = Notification.Types.CRITICAL.value
            notification.header = (
                "Alert system was not able to proceed the slack message"
            )
            notification.text = "See logs for more information"
            self.notify_alert_system_error(notification)
            raise

    def send_email_raw(self, dict_request):
        """
        Raw send email.

        :param dict_request:
        :return:
        """

        self.aws_api.sesv2_client.send_email_raw(Region.get_region(self.configuration.region), dict_request)

    class UnknownTagError(ValueError):
        """
        Can not find the tag in the routes mapping.

        """
