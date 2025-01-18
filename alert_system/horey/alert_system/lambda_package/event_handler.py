"""
Event Handler.
"""

from horey.alert_system.lambda_package.message_dispatcher import MessageDispatcher
from horey.alert_system.lambda_package.message_factory import MessageFactory
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy
from horey.alert_system.lambda_package.message_event_bridge_default import MessageEventBridgeDefault


from horey.h_logger import get_logger
logger = get_logger()


class EventHandler:
    """
    Class handling the received events.

    """

    def __init__(self, configuration_file_full_path):
        configuration = AlertSystemConfigurationPolicy()
        configuration.configuration_file_full_path = configuration_file_full_path
        configuration.init_from_file()

        self.message_factory = MessageFactory(configuration)
        self.message_dispatcher = MessageDispatcher(configuration)

    def handle_event(self, event):
        """
        Handle the received event.

        @param event:
        @return:
        """

        message = None

        try:
            message = self.message_factory.generate_message(event)
            if isinstance(message, MessageEventBridgeDefault):
                return self.message_dispatcher.run_dynamodb_update_routine()
            try:
                alarm_name, alarm_epoch_utc = message.generate_cooldown_trigger_name_and_epoch_timestamp()
                self.message_dispatcher.update_dynamodb_alarm(alarm_name, alarm_epoch_utc)
            except message.NoCooldown:
                pass
        except Exception as inst_error:
            data = message if message is not None else event
            self.message_dispatcher.handle_exception(inst_error, data)

        return self.message_dispatcher.dispatch(message)
