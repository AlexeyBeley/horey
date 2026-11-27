import pdb
import json
from enum import Enum


class SlackMessage:
    MARKS_MAPPINGS = {
        "INFO": ":information_source:",
        "STABLE": ":white_check_mark:",
        "WARNING": ":warning:",
        "CRITICAL": ":bangbang:",
        "PARTY": ":tada:",
    }

    SECTION_MARKS_MAPPINGS = {
        "CRITICAL": ":exclamation:",
        "INFO": ":bulb:",
        "STABLE": ":bee:",
        "WARNING": ":mega:",
        "PARTY": ":clinking_glasses:",
    }

    SECONDARY_MARKS_MAPPINGS = {
        "CRITICAL": ":red_circle:",
        "INFO": ":radio_button:",
        "STABLE": ":large_green_circle:",
        "WARNING": ":large_yellow_circle:",
        "PARTY": ":large_purple_circle:",
    }

    COLOR_MAPPINGS = {
        "CRITICAL": "danger",
        "INFO": "#454442",
        "STABLE": "#7CD197",
        "WARNING": "#d1d07c",
        "PARTY": "#d40fb9",
    }

    def __init__(self, message_type=None):
        self._type = None
        self.src_username = None
        self.dst_channel = None
        self._text_color = None
        self._icon_emoji = None
        self._blocks = []
        self._attachments = []
        self.message_type = message_type

    def add_block(self, block):
        block.message_type = self.message_type
        self._blocks.append(block)

        divider_block = self.DividerBlock(self.message_type)
        self._blocks.append(divider_block)

    def add_attachment(self, attachment):
        attachment.message_type = self.message_type
        self._attachments.append(attachment)

    def generate_send_request(self):
        blocks = []
        for i in range(len(self._blocks)):
            block = self._blocks[i]

            if block.block_type == "section" and block.link is not None:
                if len(blocks) > 0 and blocks[-1]["type"] == "divider":
                    blocks[-1] = block.generate_send_request()
                    continue

            blocks.append(block.generate_send_request())

        attachments = []
        for attachment in self._attachments:
            attachments.append(attachment.generate_send_request())

        slack_data = {
            "blocks": blocks,
            "channel": self.dst_channel,
            "username": self.src_username,
            "icon_emoji": self.icon_emoji,
            "attachments": attachments,
        }

        return json.dumps(slack_data)

    def init_from_dict(self, dict_src):
        pdb.set_trace()

    @property
    def type(self):
        if self._type is None:
            raise ValueError("type was not set")
        return self._type

    @type.setter
    def type(self, value):
        if not isinstance(value, self.Types):
            raise ValueError(
                f"type must be {self.Types} received {value} of type: {type(value)}"
            )

        self._type = value

    @property
    def icon_emoji(self):
        if self._icon_emoji is None:
            self._icon_emoji = self.MARKS_MAPPINGS[self.message_type.value]
        return self._icon_emoji

    @icon_emoji.setter
    def icon_emoji(self, value):
        if not isinstance(value, str):
            raise ValueError(
                f"icon_emoji must be string received {value} of icon_emoji: {type(value)}"
            )

        self._icon_emoji = value

    class Types(Enum):
        INFO = "INFO"
        STABLE = "STABLE"
        WARNING = "WARNING"
        CRITICAL = "CRITICAL"
        PARTY = "PARTY"

    class Attachment:
        def __init__(self):
            self.message_type = None
            self.text = None
            self.link_text = None

        def add_link(self, link_text, link):
            self.text += "\n" + f"<{link}|{link_text}>"

        def generate_send_request(self):
            return {
                "text": SlackMessage.SECTION_MARKS_MAPPINGS[self.message_type.value]
                + self.text,
                "color": SlackMessage.COLOR_MAPPINGS[self.message_type.value],
            }

    class Block:
        def __init__(self, message_type):
            self.message_type = message_type
            self._text = None
            self._link = None

        @property
        def text(self):
            return self._text

        @text.setter
        def text(self, value):
            if not isinstance(value, str):
                raise ValueError(
                    f"Slack Message text must be string. Got: {type(value)}: {value}"
                )
            self._text = value

        @property
        def link(self):
            return self._link

        @link.setter
        def link(self, value):
            if not isinstance(value, str):
                raise ValueError(
                    f"Slack Message link must be string. Got: {type(value)}: {value}"
                )
            self._link = value

    class SectionBlock(Block):
        def __init__(self, message_type=None):
            self.block_type = "section"
            super().__init__(message_type)

        def generate_send_request(self):
            if self.link is not None:
                return self.generate_send_request_mrkdwn_link()
            return self.generate_send_request_mrkdwn()

        def generate_send_request_mrkdwn_link(self):
            return {
                "type": self.block_type,
                "text": {"type": "mrkdwn", "text": f"<{self.link}|{self.text}>"},
            }

        def generate_send_request_mrkdwn(self):
            try:
                return {
                    "type": self.block_type,
                    "text": {
                        "type": "mrkdwn",
                        "text": SlackMessage.SECTION_MARKS_MAPPINGS[
                            self.message_type.value
                        ]
                        + self.text,
                    },
                }

            except Exception as inst:
                return {"error parsing": f"{str(self.__dict__)} self.text: {self.text}"}

    class HeaderBlock(Block):
        def __init__(self, message_type=None):
            self.block_type = "header"
            super().__init__(message_type)

        def generate_send_request(self):
            return {
                "type": self.block_type,
                "text": {
                    "type": "plain_text",
                    "text": SlackMessage.SECONDARY_MARKS_MAPPINGS[
                        self.message_type.value
                    ]
                    + self.text,
                },
            }

    class DividerBlock(Block):
        def __init__(self, message_type=None):
            self.block_type = "divider"
            super().__init__(message_type)

        def generate_send_request(self):
            return {"type": self.block_type}
