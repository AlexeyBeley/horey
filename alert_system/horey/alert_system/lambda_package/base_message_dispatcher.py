import datetime
import json
import os
import pdb
import traceback
import urllib.parse

import requests
from horey.slack_api.slack_api import SlackAPI
from horey.slack_api.slack_api_configuration_policy import SlackAPIConfigurationPolicy
from horey.slack_api.slack_message import SlackMessage

from horey.h_logger import get_logger

logger = get_logger()


class BaseMessageDispatcher:
    def __init__(self):
        self.handler_mapper = {"cloudwatch_logs_metric_sns_alarm": self.cloudwatch_logs_metric_sns_alarm_message_handler}

    def dispatch(self, message):
        try:
            self.handler_mapper[message.type](message)
        except KeyError:
            self.default_handler(message)

    def default_handler(self, message):
        text = json.dumps(message.convert_to_dict())
        slack_message = self.generate_slack_message(SlackMessage.Types.CRITICAL, "Unhandled message in alert_system", text, None, None, "#test")
        self.send_to_slack(slack_message)

    def cloudwatch_logs_metric_sns_alarm_message_handler(self, message):
        # todo: remove
        log_group_name_encoded = self.encode_to_aws_url_format(message.data["log_group_name"])
        log_group_filter_pattern_encoded = self.encode_to_aws_url_format(message.data["log_group_filter_pattern"])
        sns_message = json.loads(message.dict_src["Records"][0]["Sns"]["Message"])
        alarm_arn = sns_message["AlarmArn"]
        region = alarm_arn.split(":")[3]

        #'2022-07-14T16:14:03.407+0000'
        time_end = datetime.datetime.strptime(sns_message["StateChangeTime"], "%Y-%m-%dT%H:%M:%S.%f%z")
        #"2022-07-15T00:15:00Z"
        search_time_end = time_end.strftime("%Y-%m-%dT%H:%M:%SZ")

        time_start = time_end - datetime.timedelta(seconds=sns_message["Trigger"]["Period"])
        search_time_start = time_start.strftime("%Y-%m-%dT%H:%M:%SZ")

        log_group_search_url = f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/{log_group_name_encoded}/log-events$3Fend$3D{search_time_end}$26filterPattern$3D{log_group_filter_pattern_encoded}$26start$3D{search_time_start}"

        if sns_message["NewStateValue"] == "OK":
            slack_message_type = SlackMessage.Types.STABLE
            header = "Cloudwatch filter back to normal"
        elif sns_message["NewStateValue"] == "ALARM":
            slack_message_type = SlackMessage.Types.CRITICAL
            header = "Cloudwatch filter"
        else:
            header = f'Unknown state: {sns_message["NewStateValue"]}'
            slack_message_type = SlackMessage.Types.CRITICAL
            pdb.set_trace()

        text = f'region:{region}\n' \
               f'Log group: {message.data["log_group_name"]}\n' \
               f'Filter pattern: {message.data["log_group_filter_pattern"]}\n\n' \
               f'{sns_message["NewStateReason"]}'
        slack_message = self.generate_slack_message(slack_message_type, header, text, log_group_search_url, "View logs in CloudWatch", "#test")
        self.send_to_slack(slack_message)

    def send_to_slack(self, slack_message: SlackMessage):
        config = SlackAPIConfigurationPolicy()
        config.configuration_file_full_path = os.environ.get("SLACK_API_CONFIGURATION_FILE")
        config.init_from_file()
        slack_api = SlackAPI(configuration=config)
        logger.info(f"Sending message to slack")
        try:
            slack_api.send_message(slack_message)
        except Exception as exception_inst:
            traceback_str = ''.join(traceback.format_tb(exception_inst.__traceback__))
            logger.exception(traceback_str)
            message = SlackMessage(message_type=SlackMessage.Types.CRITICAL)
            block = SlackMessage.HeaderBlock()
            block.text = "Alert system was not able to proceed the slack message"
            message.add_block(block)

            block = SlackMessage.SectionBlock()
            block.text = f"See logs for more information"
            message.add_block(block)

            message.src_username = "slack_api"
            message.dst_channel = slack_message.dst_channel

            slack_api.send_message(message)
            raise

    def generate_slack_message(self, slack_message_type, header, text, link, link_href, dst_channel):
        try:
            return self.generate_slack_message_helper(slack_message_type, header, text, link, link_href, dst_channel)
        except Exception as exception_inst:
            logger.exception("Slack message generation failed. Generating default message.")
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
                       f"dst_channel: '{dst_channel}'\n" + \
                       repr(exception_inst) + "\n" +\
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

        attachment = SlackMessage.Attachment()
        attachment.text = text
        if link is not None:
            attachment.add_link(link_href, link)

        message.add_attachment(attachment)

        message.src_username = "slack_api"
        message.dst_channel = dst_channel
        return message

    @staticmethod
    def encode_to_aws_url_format(str_src):
        """
        https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Fecs$252Fcontainer-name/log-events$3FfilterPattern$3D$2522$255BINFO$255D$2522

        @param str_src:
        @return:
        """

        ret = urllib.parse.quote(str_src, safe='')
        return ret.replace("%", "$25")
