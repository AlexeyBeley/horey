import json
import os
import traceback

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
        text = json.dumps(message.convert_to_dict())
        self.generate_slack_message(SlackMessage.Types.CRITICAL, "Unhandled message in alert_system", text, None, None, "#test")

    def send_to_slack(self, slack_message):
        config = SlackAPIConfigurationPolicy()
        config.configuration_file_full_path = os.environ.get("SLACK_API_CONFIGURATION_FILE")
        config.init_from_file()
        slack_api = SlackAPI(configuration=config)
        logger.info(f"Sending message to slack")
        try:
            slack_api.send_message(slack_message)
        except Exception as exception_inst:
            traceback_str = ''.join(traceback.format_tb(exception_inst.__traceback__))
            message = SlackMessage(message_type=SlackMessage.Types.CRITICAL)
            block = SlackMessage.HeaderBlock()
            block.text = "Was not able to send slack message"
            message.add_block(block)

            block = SlackMessage.SectionBlock()
            new_text = f"slack_message: '{slack_message.__dict__}'" +\
                       traceback_str

            block.text = new_text
            message.add_block(block)

            message.src_username = "slack_api"
            message.dst_channel = slack_message.dst_channel

            slack_api.send_message(message)

    def generate_slack_message(self, slack_message_type, header, text, link, link_href, dst_channel):
        try:
            return self.generate_slack_message_helper(slack_message_type, header, text, link, link_href, dst_channel)
        except Exception as exception_inst:
            traceback_str = ''.join(traceback.format_tb(exception_inst.__traceback__))
            message = SlackMessage(message_type=SlackMessage.Types.CRITICAL)
            block = SlackMessage.HeaderBlock()
            block.text = "Was not able to generate slack message"
            message.add_block(block)

            block = SlackMessage.SectionBlock()
            new_text = f"slack_message_type: '{slack_message_type}', " \
                       f"header: '{header}', " \
                       f"text: '{text}', " \
                       f"link: '{link}', " \
                       f"link_href: '{link_href}', " \
                       f"dst_channel: '{dst_channel}'\n" +\
                       traceback_str

            block.text = new_text
            message.add_block(block)

            message.src_username = "slack_api"
            message.dst_channel = dst_channel
            return message

    def generate_slack_message_helper(self, slack_message_type, header, text, link, link_href, dst_channel):
        if text is None:
            raise RuntimeError("Text param can not be None")

        message = SlackMessage(message_type=slack_message_type)
        block = SlackMessage.HeaderBlock()
        block.text = f"{slack_message_type.value}: {header}"
        message.add_block(block)

        block = SlackMessage.SectionBlock()
        block.text = text
        message.add_block(block)

        if link is not None:
            block = SlackMessage.SectionBlock()
            block.text = link_href
            block.link = link
            message.add_block(block)

        message.src_username = "slack_api"
        message.dst_channel = dst_channel
        return message
