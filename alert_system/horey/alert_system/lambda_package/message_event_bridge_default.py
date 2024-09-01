"""
Message being received by the Alert System Lambda.

"""

from horey.h_logger import get_logger
from horey.alert_system.lambda_package.message_base import MessageBase

logger = get_logger()


class MessageEventBridgeDefault(MessageBase):
    """
    Main class.

    """

    def __init__(self, dict_src, configuration):
        message_dict = MessageBase.extract_message_dict(dict_src)
        if message_dict.get("source") != "aws.events" or \
                message_dict.get("detail-type") != "Scheduled Event" or \
                message_dict.get("version") != "0":
            raise MessageBase.NotAMatchError("Wrong class")

        super().__init__(dict_src, configuration)

    def generate_notification(self):
        """
        Should not run notification.

        :return:
        """
        raise RuntimeError("Not implemented")
