import pdb

import pytest
import os

from horey.slack_api.slack_api import SlackAPI
from horey.slack_api.slack_api_configuration_policy import SlackAPIConfigurationPolicy
from horey.slack_api.slack_message import SlackMessage


configuration = SlackAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                 "slack_api_configuration_values.py"))
configuration.init_from_file()

slack_api = SlackAPI(configuration=configuration)


@pytest.mark.skip(reason="Can not test")
def test_send_message_stable():
    message = SlackMessage(SlackMessage.Types.STABLE)
    block = SlackMessage.HeaderBlock()
    block.text = "Resolved in 2m 0s: Load average is too high (per CPU load over 1.5 for 15m)"

    message.add_block(block)

    attachment = SlackMessage.Attachment()
    attachment.text = """Problem has been resolved at 10:20:00 on 2011.11.11
    Problem name: Load average is too high (per CPU load over 1.5 for 15m)
    Problem duration: 20m 0s
    Host: horey-ui-host
    Severity: Average
    Original problem ID: 8888"""
    message.add_attachment(attachment)

    block = SlackMessage.SectionBlock()
    block.text = "Zabbix problem[8888]"
    block.link = "https://example.com"
    message.add_block(block)

    block = SlackMessage.SectionBlock()
    block.text = "Jira Bug[9999]"
    block.link = "https://example.com"
    message.add_block(block)

    message.src_username = "slack_api"
    message.dst_channel = "#test"

    ret = slack_api.send_message(message)
    assert ret


@pytest.mark.skip(reason="Can not test")
def test_send_message_warning():
    message = SlackMessage(SlackMessage.Types.WARNING)

    block = SlackMessage.HeaderBlock()
    block.text = "Problem: Load average is too high (per CPU load over 1.5 for 15m)"
    message.add_block(block)

    attachment = SlackMessage.Attachment()
    attachment.text = "Problem started at 10:00:00 on 2011.11.11\n" \
                      "Problem name: Load average is too high (per CPU load over 1.5 for 15m)\n" \
                      "Host: horey-ui-host\n" \
                      "Severity: Average\n" \
                      "Operational data: Load averages(1m 5m 15m): (4.42 3.41 2.78), # of CPUs: 2\n" \
                      "Original problem ID: 8888"

    message.add_attachment(attachment)

    block = SlackMessage.SectionBlock()
    block.text = "Zabbix dashboard"
    block.link = "https://example.com"
    message.add_block(block)

    message.src_username = "slack_api"
    message.dst_channel = "#test"

    ret = slack_api.send_message(message)
    assert ret


@pytest.mark.skip(reason="Can not test")
def test_send_message_critical():
    message = SlackMessage(SlackMessage.Types.CRITICAL)

    block = SlackMessage.HeaderBlock()
    block.text = "CRITICAL: User experience impact"
    message.add_block(block)

    block = SlackMessage.SectionBlock()
    block.text = "Metric: UI loading in APAC has dropped below 100ms"
    message.add_block(block)

    block = SlackMessage.SectionBlock()
    block.text = "Grafana dashboard"
    block.link = "https://example.com"
    message.add_block(block)

    message.src_username = "slack_api"
    message.dst_channel = "#test"

    ret = slack_api.send_message(message)
    assert ret


@pytest.mark.skip(reason="Can not test")
def test_send_message_info():
    message = SlackMessage(SlackMessage.Types.INFO)

    block = SlackMessage.HeaderBlock()
    block.text = "INFO: Merged to master"
    message.add_block(block)

    block = SlackMessage.SectionBlock()
    block.text = "Component UI master was updated"
    message.add_block(block)

    block = SlackMessage.SectionBlock()
    block.text = "PR[2020]"
    block.link = "https://example.com"
    message.add_block(block)

    message.src_username = "slack_api"
    message.dst_channel = "#test"

    ret = slack_api.send_message(message)
    assert ret


@pytest.mark.skip(reason="Can not test")
def test_send_message_party():
    message = SlackMessage(SlackMessage.Types.PARTY)

    block = SlackMessage.HeaderBlock()
    block.text = "PARTY: Deployed to prod"
    message.add_block(block)

    block = SlackMessage.SectionBlock()
    block.text = "Component UI was deployed successfully to production"
    message.add_block(block)

    block = SlackMessage.SectionBlock()
    block.text = "Build[1010]"
    block.link = "https://example.com"
    message.add_block(block)

    message.src_username = "slack_api"
    message.dst_channel = "#test"

    ret = slack_api.send_message(message)
    assert ret


# endregion


if __name__ == "__main__":
    test_send_message_warning()
    test_send_message_critical()
    test_send_message_info()
    test_send_message_party()
    test_send_message_stable()
