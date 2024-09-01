"""
Message being received by the Alert System Lambda.

"""

from horey.h_logger import get_logger
from horey.alert_system.lambda_package.message_cloudwatch_default import MessageCloudwatchDefault
from horey.alert_system.lambda_package.message_ses_default import MessageSESDefault
from horey.alert_system.lambda_package.message_event_bridge_default import MessageEventBridgeDefault
from horey.alert_system.lambda_package.message_base import MessageBase
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy
from horey.common_utils.common_utils import CommonUtils

logger = get_logger()


class MessageFactory:
    """
    Main class.

    """

    def __init__(self, configuration: AlertSystemConfigurationPolicy):
        self.configuration = configuration
        self.message_classes = self.load_message_classes() + [MessageEventBridgeDefault,  MessageCloudwatchDefault, MessageSESDefault]

    def load_message_classes(self):
        """
        Load explicitly set message classes from files provided in configuration.

        :return:
        """

        if self.configuration.message_classes:
            return [self.load_message_class(file_path) for file_path in self.configuration.message_classes]

        return []

    @staticmethod
    def load_message_class(initializer_file_path):
        """
        Init notification channel from initializer file path

        :param initializer_file_path:
        :return:
        """

        message_class = CommonUtils.load_object_from_module(initializer_file_path, "main")
        return message_class

    def generate_message(self, dict_event):
        """
        Generate message from event

        :param dict_event:
        :return:
        """

        for message_class in self.message_classes:
            try:
                return message_class(dict_event, self.configuration)
            except MessageBase.NotAMatchError:
                pass
        raise ValueError(f"Can not find message generator for event: {dict_event}")
