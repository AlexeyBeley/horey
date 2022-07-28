import json
import os
import pdb

from message import Message

from horey.h_logger import get_logger
try:
    from message_dispatcher import MessageDispatcher
except ModuleNotFoundError:
    from message_dispatcher_base import MessageDispatcherBase as MessageDispatcher

logger = get_logger()


class EventHandler:
    def __init__(self):
        self.message_dispatcher = MessageDispatcher()

    def handle_event(self, event, context):
        message = self.extract_message(event)
        self.message_dispatcher.dispatch(message)

    def extract_message(self, event):
        if "Records" in event:
            return self.extract_message_records(event)
        raise NotImplementedError(event)

    def extract_message_records(self, event):
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

        message.init_from_dict(dict_src)
        return message


def lambda_handler(event, context):
    """
    
    :param event:
    :param context:
    :return:
    """
    logger.info(f"Handling event: '{json.dumps(event)}'")

    event_handler = EventHandler()
    event_handler.handle_event(event, context)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
