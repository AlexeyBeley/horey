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

        errors = []
        notification = Notification()
        text = self.message_dict.get("text")
        if text is None:
            errors.append("Value 'text' was not received in message")

        str_type = self.message_dict.get("type")
        if not str_type:
            errors.append("Value 'type' was not received in message, setting explicitly to CRITICAL")
            str_type = "CRITICAL"

        notification.text = " ".join(errors) + f" {self.message_dict=}" if errors else text
        notification.type = Notification.Types.__members__.get(str_type)

        notification.header = self.message_dict.get("header", "Default header")
        for attr in ["link", "link_href", "routing_tags"]: 
            if value := self.message_dict.get(attr):
                setattr(notification, attr, value)
        return notification
