"""
Message being received by the Alert System Lambda.

"""

from horey.h_logger import get_logger
from horey.alert_system.lambda_package.message_cloudwatch_default import MessageCloudwatchDefault
from horey.alert_system.lambda_package.message_ses_default import MessageSESDefault
from horey.alert_system.lambda_package.message_zabbix_default import MessageZabbixDefault
from horey.alert_system.lambda_package.message_base import MessageBase

logger = get_logger()


class MessageFactory:
    """
    Main class.

    """

    def __init__(self, configuration):
        self.configuration = configuration
        self.message_classes = [MessageCloudwatchDefault, MessageSESDefault, MessageZabbixDefault]

    def generate_message(self, dict_event):
        """
        Generate message from event

        :param dict_event:
        :return:
        """

        for message_class in self.message_classes:
            try:
                return message_class(dict_event)
            except MessageBase.NotAMatchError:
                pass
        raise ValueError(f"Can not find message generator for event: {dict_event}")
