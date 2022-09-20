"""
Entry point for the receiver lambda.

"""

import json
import traceback

from message import Message

from horey.h_logger import get_logger
try:
    from message_dispatcher import MessageDispatcher
except ModuleNotFoundError:
    from message_dispatcher_base import MessageDispatcherBase as MessageDispatcher

logger = get_logger()


class EventHandler:
    """
    Class handling the received events.

    """

    def __init__(self):
        self.message_dispatcher = MessageDispatcher()

    def handle_event(self, event):
        """
        Handle the received event.

        @param event:
        @return:
        """

        message = self.extract_message(event)
        self.message_dispatcher.dispatch(message)

    def extract_message(self, event):
        """
        Build Message object from the event dictionary.

        @param event:
        @return:
        """

        if "Records" in event:
            return self.extract_message_records(event)
        raise NotImplementedError(event)

    @staticmethod
    def extract_message_records(event):
        """
        For cloudwatch message - convert records to Message objects.

        @param event:
        @return:
        """

        if len(event["Records"]) != 1:
            raise RuntimeError(event)

        record = event["Records"][0]
        if record["EventSource"] != "aws:sns":
            raise NotImplementedError(event)
        message_dict = json.loads(record["Sns"]["Message"])
        message = Message(dic_src=event)
        if "AlarmDescription" in message_dict:
            dict_src = json.loads(message_dict["AlarmDescription"])
        else:
            dict_src = message_dict

        try:
            del dict_src["dict_src"]
        except KeyError:
            pass
        try:
            message.init_from_dict(dict_src)
        except Exception as error_inst:
            traceback_str = ''.join(traceback.format_tb(error_inst.__traceback__))
            logger.exception(f"{traceback_str}\n{repr(error_inst)}")

        return message


def lambda_handler(event, _):
    """
    Entry point for this lambda

    :param event:
    :param _: context
    :return:
    """
    logger_string = json.dumps(event)
    if "log_group_filter_pattern" in logger_string:
        try:
            filter_string_start_index = logger_string.index("log_group_filter_pattern")
            filter_string_start_index = logger_string.index(r': \\\"', filter_string_start_index) + 6
            filter_string_end_index = logger_string.index(r'\\\"}, \\\"type\\\":', filter_string_start_index)
            logger_string = logger_string[:filter_string_start_index] + "filter_string_removed_to_exclude_recursion" + logger_string[filter_string_end_index:]
        except Exception as error_inst:
            traceback_str = ''.join(traceback.format_tb(error_inst.__traceback__))
            logger.exception(f"{traceback_str}\n{repr(error_inst)}")

    logger.info(f"Handling event: '{logger_string}'")

    event_handler = EventHandler()
    event_handler.handle_event(event)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
