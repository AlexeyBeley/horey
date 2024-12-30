"""
Message being received by the Alert System Lambda.

"""

from horey.h_logger import get_logger
from horey.alert_system.lambda_package.message_base import MessageBase
from horey.alert_system.lambda_package.notification import Notification
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy


logger = get_logger()


class MessageRaw(MessageBase):
    """
    Main class.

    """

    def __init__(self, dict_src, configuration):
        """
        Try to init from dict

        :param dict_src:
        :return:
        """

        super().__init__(dict_src, configuration)
        try:
            self.message_dict = MessageBase.extract_message_dict(dict_src)
        except Exception as inst_error:
            raise MessageBase.NotAMatchError(f"Not a match {repr(inst_error)}")

        if self.message_dict.get("notificationType") == "AmazonSnsSubscriptionSucceeded":
            return

        if AlertSystemConfigurationPolicy.ALERT_SYSTEM_RAW_MESSAGE_KEY not in self.message_dict:
            raise MessageBase.NotAMatchError("Not a match")

    # pylint: disable = too-many-statements
    def generate_notification(self):
        """
        Generate notification from message.

        :return:
        """

        notification = Notification()

        notification.type = Notification.Types.CRITICAL
        breakpoint()
        notification.text = self.message_dict["text"]
        notification.header = self.message_dict["header"]
        notification.link = self.message_dict["link"]
        notification.link_href = self.message_dict["link_href"]
        notification.routing_tags = self.message_dict["routing_tags"]
        return notification
