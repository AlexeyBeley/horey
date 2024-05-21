"""
Message being received by the Alert System Lambda.

"""

from horey.h_logger import get_logger
from horey.alert_system.lambda_package.message_base import MessageBase
from horey.alert_system.lambda_package.notification import Notification


logger = get_logger()


class MessageSESDefault(MessageBase):
    """
    Main class.

    """

    @staticmethod
    def init_from_dict(dict_src):
        """
        Try to init from dict

        :param dict_src:
        :return:
        """

        message_dict = MessageBase.extract_message_dict(dict_src)
        if "mail" not in message_dict:
            raise MessageBase.NotAMatchError("Not a match")

        return MessageSESDefault(dict_src)

    def generate_notification(self):
        """
        Generate notification from message.

        :return:
        """
        notification = Notification()
        breakpoint()
