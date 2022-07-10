import json
import pdb

from .message import Message
from .message_dispatcher import MessageDispatcher

from horey.h_logger import get_logger

logger = get_logger()


class MessageHandler:
    def __init__(self):
        self.message_dispatcher = MessageDispatcher()

    def handle_message(self, event, context):
        message = self.extract_message(event)
        self.message_dispatcher.dispatch(message)

    def extract_message(self, event):
        if "Records" in event:
            return self.extract_message_cloudwatch(event)
        raise NotImplementedError(event)

    def extract_message_cloudwatch(self, event):
        if len(event["Records"]) != 1:
            raise RuntimeError(event)
        record = event["Records"][0]
        if record["EventSource"] != "aws:sns":
            raise NotImplementedError(event)
        message_dict = json.loads(record["Sns"]["Message"])
        message = Message(event)
        message.init_from_dict(json.loads(message_dict["AlarmDescription"]))
        return message


def lambda_handler(event, context):
    """
    
    :param event:
    :param context:
    :return:
    """
    message_handler = MessageHandler()
    message_handler.handle_message(event, context)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
