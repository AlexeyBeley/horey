from notification_channel_base import NotificationChannelBase
from notification import Notification
from horey.slack_api.slack_message import SlackMessage


class NotificationChannelSlack(NotificationChannelBase):
    CONFIGURATION_POLICY_FILE_NAME = "notification_channel_slack_configuration_policy.py"
    CONFIGURATION_POLICY_CLASS_NAME = "NotificationChannelSlackConfigurationPolicy"

    def __init__(self, configuration):
        super().__init__(configuration)

    def send_notifications(self, notification_type, header, text, link, link_href, routing_tags):
        for routing_tag in routing_tags:
            Notification.Tyes.get()
            slack_message_type = SlackMessage.Types.get(notification_type.value)
            SlackMessage(message_type=slack_message_type)




