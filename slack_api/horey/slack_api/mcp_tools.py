"""
MCP tools of horey.slack_api. Loaded by horey.mcp, see mcp/README.md.
"""

import functools
from typing import TYPE_CHECKING

from horey.slack_api.slack_api import SlackAPI
from horey.slack_api.slack_api_configuration_policy import SlackAPIConfigurationPolicy
from horey.slack_api.slack_message import SlackMessage

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    @functools.cache
    def slack_api() -> SlackAPI:
        return SlackAPI(registry.get_configuration(SlackAPIConfigurationPolicy))

    @registry.tool()
    def send_message(channel: str, header: str, text: str = "", message_type: str = "INFO",
                     links: dict[str, str] | None = None, username: str = "horey") -> bool:
        """
        Send a message to a Slack channel: a header, an optional text (Slack mrkdwn) and optional links {text: url}.
        message_type sets the icon and the color: INFO, STABLE, WARNING, CRITICAL or PARTY.
        """
        message = SlackMessage(SlackMessage.Types(message_type))

        header_block = SlackMessage.HeaderBlock()
        header_block.text = header
        message.add_block(header_block)

        if text:
            attachment = SlackMessage.Attachment()
            attachment.text = text
            message.add_attachment(attachment)

        for link_text, link in (links or {}).items():
            link_block = SlackMessage.SectionBlock()
            link_block.text = link_text
            link_block.link = link
            message.add_block(link_block)

        message.src_username = username
        message.dst_channel = channel
        return bool(slack_api().send_message(message))
