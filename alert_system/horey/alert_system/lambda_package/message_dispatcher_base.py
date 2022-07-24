import datetime
import json
import os
import pdb
import traceback
import urllib.parse

import requests
from alert_system_message_router import AlertSystemMessageRouter
from horey.slack_api.slack_api import SlackAPI
from horey.slack_api.slack_api_configuration_policy import SlackAPIConfigurationPolicy
from horey.slack_api.slack_message import SlackMessage

from horey.h_logger import get_logger

logger = get_logger()


class MessageDispatcherBase:
    def __init__(self, system_alerts_slack_channel=None):
        self.handler_mapper = {"cloudwatch_logs_metric_sns_alarm": self.cloudwatch_logs_metric_sns_alarm_message_handler}
        self.router = AlertSystemMessageRouter(system_alerts_slack_channel=system_alerts_slack_channel)

    def get_message_types(self):
        return list(self.handler_mapper.keys())

    def dispatch(self, message):
        try:
            self.handler_mapper[message.type](message)
        except KeyError:
            self.default_handler(message)

    def default_handler(self, message):
        try:
            alarms = self.split_sns_message_to_alarms(message)
            self.handle_cloudwatch_alarm_default(alarms)
            return
        except Exception as error_inst:
            logger.exception(error_inst)

        text = json.dumps(message.convert_to_dict())
        for channel in self.get_slack_channels(message):
            slack_message = self.generate_slack_message(SlackMessage.Types.CRITICAL, "Unhandled message in alert_system", text, None, None, channel)
            self.send_to_slack(slack_message)

    def handle_cloudwatch_alarm_default(self, alarms):
        for alarm in alarms:
            self._handle_cloudwatch_alarm(alarm)

    def cloudwatch_logs_metric_sns_alarm_message_handler(self, message):
        alarms = self.split_sns_message_to_alarms(message)
        for alarm in alarms:
            self.handle_cloudwatch_logs_metric_alarm(alarm)

    def split_sns_message_to_alarms(self, message):
        return [CloudwatchAlarm(record_dict) for record_dict in message.dict_src["Records"]]

    def handle_cloudwatch_logs_metric_alarm(self, alarm):
        self._handle_cloudwatch_logs_metric_alarm(alarm)

    def _handle_cloudwatch_logs_metric_alarm(self, alarm, slack_header=None, slack_message_type=None, slack_text=None):
        log_group_search_url = self.generate_cloudwatch_log_search_link(alarm, alarm.alert_system_data["log_group_name"], alarm.alert_system_data["log_group_filter_pattern"])
        if slack_text is None:
            slack_text = f'region:{alarm.region}\n' \
               f'Log group: {alarm.alert_system_data["log_group_name"]}\n' \
               f'Filter pattern: {alarm.alert_system_data["log_group_filter_pattern"]}\n\n' \
               f'{alarm.new_state_reason}'

        self._handle_cloudwatch_alarm(alarm, slack_header=slack_header, slack_message_type=slack_message_type, slack_text=slack_text, alarm_url=log_group_search_url, alarm_url_href="View logs in CloudWatch")

    def _handle_cloudwatch_alarm(self, alarm, slack_header=None, slack_message_type=None, slack_text=None, alarm_url=None, alarm_url_href=None):
        if slack_message_type is None:
            if alarm.new_state == "OK":
                slack_message_type = SlackMessage.Types.STABLE
                slack_header = slack_header or "Default handler: Cloudwatch alarm back to normal"
            elif alarm.new_state == "ALARM":
                slack_message_type = SlackMessage.Types.CRITICAL
                slack_header = slack_header or "Default handler: Cloudwatch alarm triggered"
            else:
                slack_header = f'Unknown state: {alarm.new_state}'
                slack_message_type = SlackMessage.Types.CRITICAL

        if slack_text is None:
            slack_text = f'*{alarm.sns_message["AlarmName"]}*\n' \
                         f'Region: {alarm.region}\n\n>' \
                         f'Reason: {alarm.new_state_reason}\n\n' \
                         f'Description: {alarm.sns_message["AlarmDescription"]}'

        for channel in self.get_slack_channels(None, alarm=alarm):
            slack_message = self.generate_slack_message(slack_message_type, slack_header, slack_text, alarm_url, alarm_url_href, channel)
            self.send_to_slack(slack_message)

    def generate_cloudwatch_log_search_link(self, alarm, log_group_name, log_group_filter_pattern, ):
        log_group_name_encoded = self.encode_to_aws_url_format(log_group_name)
        log_group_filter_pattern_encoded = self.encode_to_aws_url_format(log_group_filter_pattern)

        search_time_end = alarm.end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        search_time_start = alarm.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        log_group_search_url = f"https://{alarm.region}.console.aws.amazon.com/cloudwatch/home?region={alarm.region}#logsV2:log-groups/log-group/{log_group_name_encoded}/log-events$3Fend$3D{search_time_end}$26filterPattern$3D{log_group_filter_pattern_encoded}$26start$3D{search_time_start}"
        return log_group_search_url

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

    def get_slack_channels(self, message, alarm=None):
        try:
            slack_channels = self.router.get_slack_routes(message, alarm=alarm)
        except self.router.UnknownTag as exception_inst:
            logger.exception(f"{repr(exception_inst)}\n{''.join(traceback.format_tb(exception_inst.__traceback__))}")
            slack_channels = [self.router.system_alerts_slack_channel]
        return slack_channels


class CloudwatchAlarm:
    def __init__(self, dict_src):
        self.dict_src = dict_src
        self._sns_message = None
        self._alert_system_data = None
        self._start_time = None
        self._end_time = None

    @property
    def sns_message(self):
        if self._sns_message is None:
            self._sns_message = json.loads(self.dict_src["Sns"]["Message"])
        return self._sns_message

    @property
    def region(self):
        return self.sns_message["AlarmArn"].split(":")[3]

    @property
    def alert_system_data(self):
        if self._alert_system_data is None:
            self._alert_system_data = json.loads(self.sns_message["AlarmDescription"])["data"]
        return self._alert_system_data

    @property
    def start_time(self):
        """
        2022-07-14T16:14:03.407+0000

        @return:
        """
        if self._start_time is None:
            self._start_time = self.end_time - datetime.timedelta(seconds=self.sns_message["Trigger"]["Period"])
        return self._start_time

    @property
    def end_time(self):
        if self._end_time is None:
            self._end_time = datetime.datetime.strptime(self.sns_message["StateChangeTime"], "%Y-%m-%dT%H:%M:%S.%f%z")
        return self._end_time

    @property
    def new_state(self):
        return self.sns_message["NewStateValue"]

    @property
    def new_state_reason(self):
        return self.sns_message["NewStateReason"]

