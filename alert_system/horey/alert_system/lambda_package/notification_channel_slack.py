import pdb
import os
import traceback

from notification_channel_base import NotificationChannelBase
from notification import Notification
from horey.slack_api.slack_message import SlackMessage
from horey.slack_api.slack_api_configuration_policy import SlackAPIConfigurationPolicy
from horey.slack_api.slack_api import SlackAPI

from horey.h_logger import get_logger

logger = get_logger()


class NotificationChannelSlack(NotificationChannelBase):
    CONFIGURATION_POLICY_FILE_NAME = "notification_channel_slack_configuration_policy.py"
    CONFIGURATION_POLICY_CLASS_NAME = "NotificationChannelSlackConfigurationPolicy"

    def __init__(self, configuration):
        super().__init__(configuration)
        config = SlackAPIConfigurationPolicy()
        config.configuration_file_full_path = configuration.CONFIGURATION_FILE_NAME
        config.init_from_file()
        self.configuration = configuration
        self.slack_api = SlackAPI(configuration=config)

    def notify(self, notification: Notification):
        pdb.set_trace()
        for routing_tag in notification.tags:
            for dst_channel in self.map_routing_tag_to_channels(routing_tag):
                Notification.Types.get()
                slack_message_type = SlackMessage.Types.get(notification.type.value)
                slack_message = self.generate_slack_message(slack_message_type, notification.header,
                                                               notification.text, notification.link,
                                                               notification.link_href,
                                                               dst_channel)
                self.send(slack_message)

    def map_routing_tag_to_channels(self, tag):
        return tag

    def notify_alert_system_error(self, notification: Notification):
        slack_message = self.generate_slack_message(SlackMessage.Types.CRITICAL, notification.header, notification.text,
                                                           notification.link, notification.link_href,
                                                           self.configuration.alert_system_monitoring_channel)
        self.send(slack_message)

    def send(self, slack_message):
        logger.info(f"Sending message to slack")
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

    @staticmethod
    def generate_slack_message(slack_message_type, header, text, link, link_href, dst_channel):
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

        message.src_username = "slack_api"
        message.dst_channel = dst_channel
        return message
