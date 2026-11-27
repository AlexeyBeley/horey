"""
Shamelessly stolen from:
https://github.com/lukecyca/pyslack

"""

import requests
from horey.h_logger import get_logger
from horey.slack_api.slack_api_configuration_policy import SlackAPIConfigurationPolicy
from horey.slack_api.slack_message import SlackMessage

logger = get_logger()


class SlackAPI:
    """
    Slack API

    """

    def __init__(self, configuration: SlackAPIConfigurationPolicy = None):
        self.webhook_url = configuration.webhook_url
        self.bearer_token = configuration.bearer_token

    def send_message(self, message: SlackMessage):
        """
        Send message to slack.

        :param message:
        :return:
        """

        if self.bearer_token:
            return self.send_message_app(message)
        return self.send_message_webhook(message)

    def send_message_app(self, message: SlackMessage):
        """

        :param message:
        :return:
        """

        logger.info(f"Sending message using Slack APP to '{message.dst_channel}' from '{message.src_username}'")

        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            data=message.generate_send_request(),
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {self.bearer_token}"},
            timeout=60
        )
        if response.status_code != 200:
            raise ValueError(
                f"Request to slack returned an error {response.status_code}, the response is:\n{response.text}"
            )

        return True

    def send_message_webhook(self, message: SlackMessage):
        """
        Send message using webhook

        :param message:
        :return:
        """
        logger.info("Sending message using webhook")

        response = requests.post(
            self.webhook_url,
            data=message.generate_send_request(),
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        if response.status_code != 200:
            raise ValueError(
                f"Request to slack returned an error {response.status_code}, the response is:\n{response.text}"
            )

        return True
