"""
Notification Channel to send slack messages.

"""

import traceback

from notification_channel_base import NotificationChannelBase
from notification import Notification

from horey.slack_api.slack_message import SlackMessage
from horey.slack_api.slack_api_configuration_policy import SlackAPIConfigurationPolicy
from horey.slack_api.slack_api import SlackAPI
from horey.h_logger import get_logger

logger = get_logger()


class NotificationChannelSlack(NotificationChannelBase):
    """
    Main class.

    """

    CONFIGURATION_POLICY_FILE_NAME = "notification_channel_slack_configuration_policy.py"
    CONFIGURATION_POLICY_CLASS_NAME = "NotificationChannelSlackConfigurationPolicy"

    def __init__(self, configuration):
        super().__init__(configuration)
        config = SlackAPIConfigurationPolicy()
        config.init_from_policy(configuration, ignore_undefined=True)
        self.configuration = configuration
        self.slack_api = SlackAPI(configuration=config)

    def notify(self, notification: Notification):
        """
        Send the notification to relevant channels.

        @param notification:
        @return:
        """

        if notification.type not in Notification.Types:
            notification.text = f"Error in notification type. Auto set to CRITICAL: " \
                                f"received {str(notification.type)} must be one of {list(Notification.Types)}.\n" \
                                f"Original message {notification.text}"
            notification.type = Notification.Types.CRITICAL

        for routing_tag in notification.tags:
            for dst_channel in self.map_routing_tag_to_channels(routing_tag):
                slack_message_type = getattr(SlackMessage.Types, notification.type.value)
                slack_message = self.generate_slack_message(slack_message_type, notification.header,
                                                               notification.text, notification.link,
                                                               notification.link_href,
                                                               dst_channel)
                self.send(slack_message)

    def map_routing_tag_to_channels(self, tag):
        """
        Find matching channels to this routing tag.

        @param tag:
        @return:
        """
        routes = self.configuration.tag_to_channel_mapping[tag]
        if isinstance(routes, str):
            routes = [routes]

        return routes

    def notify_alert_system_error(self, notification: Notification):
        """
        Notify self monitoring problem.

        @param notification:
        @return:
        """

        slack_message = self.generate_slack_message(SlackMessage.Types.CRITICAL, notification.header, notification.text,
                                                           notification.link, notification.link_href,
                                                           self.configuration.alert_system_monitoring_destination)
        self.send(slack_message)

    def send(self, slack_message):
        """
        Send slack message to slack

        @param slack_message:
        @return:
        """

        logger.info("Sending message to slack")
        try:
            self.slack_api.send_message(slack_message)
        except Exception as exception_inst:
            traceback_str = ''.join(traceback.format_tb(exception_inst.__traceback__))
            logger.exception(traceback_str)

            notification = Notification()
            notification.header = "Alert system was not able to proceed the slack message"
            notification.text = "See logs for more information"
            self.notify_alert_system_error(notification)
            raise

    # pylint: disable=too-many-arguments
    @staticmethod
    def generate_slack_message(slack_message_type, header, text, link, link_href, dst_channel):
        """
        Generate slack message to be sent.

        @param slack_message_type:
        @param header:
        @param text:
        @param link:
        @param link_href:
        @param dst_channel:
        @return:
        """

        if text is None:
            raise RuntimeError("Text param can not be None")

        message = SlackMessage(message_type=slack_message_type)
        block = SlackMessage.HeaderBlock()
        block.text = f"{slack_message_type.value}: {header}"
        message.add_block(block)

        attachment = SlackMessage.Attachment()
        attachment.text = text
        if link is not None:
            attachment.add_link(link_href, link)

        message.add_attachment(attachment)

        message.src_username = "alert_system"
        message.dst_channel = dst_channel
        return message
