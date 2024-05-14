"""
Message being received by the Alert System Lambda.

"""

from horey.h_logger import get_logger
from horey.alert_system.lambda_package.message_base import MessageBase

logger = get_logger()


class MessageZabbixDefault(MessageBase):
    """
    Main class.

    """

    @classmethod
    def init_from_dict(cls, dict_src):
        """
        Try to init from dict

        :param dict_src:
        :return:
        """

        message_dict = MessageBase.extract_message_dict(dict_src)
        if message_dict.get("alert_system_message_class") == cls.__name__:
            return MessageZabbixDefault(dict_src)

        raise MessageBase.NotAMatchError("Wrong class")
