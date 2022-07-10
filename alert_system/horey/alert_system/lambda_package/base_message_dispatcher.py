import json
import os
import pdb

import requests
from horey.slack_api.slack_api import SlackAPI
from horey.slack_api.slack_api_configuration_policy import SlackAPIConfigurationPolicy
from horey.slack_api.slack_message import SlackMessage

from horey.h_logger import get_logger

logger = get_logger()


class BaseMessageDispatcher:
    def __init__(self):
        self.handler_mapper = dict()

    def dispatch(self, message):
        try:
            self.handler_mapper[message.type](message)
        except KeyError:
            self.default_handler(message)

    def default_handler(self, message):
        pdb.set_trace()
        self.generate_slack_message(SlackMessage.Types.CRITICAL, "test", "test", None, None, "#test")

    def send_to_slack(self, slack_message):
        config = SlackAPIConfigurationPolicy()
        config.configuration_file_full_path = os.environ.get("SLACK_API_CONFIGURATION_FILE")
        config.init_from_file()
        slack_api = SlackAPI(configuration=config)
        logger.info(f"Sending message to slack")
        ret = slack_api.send_message(slack_message)

    def generate_slack_message(self, slack_message_type, header, text, link, link_href, dst_channel):
        message = SlackMessage(message_type=slack_message_type)

        block = SlackMessage.HeaderBlock()
        block.text = f"{slack_message_type.value}: {header}"
        message.add_block(block)

        block = SlackMessage.SectionBlock()
        block.text = text
        message.add_block(block)

        block = SlackMessage.SectionBlock()
        block.text = link_href
        block.link = link
        message.add_block(block)

        message.src_username = "slack_api"
        message.dst_channel = dst_channel
        self.send_to_slack(message)
