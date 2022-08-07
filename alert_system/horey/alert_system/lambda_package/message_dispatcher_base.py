import datetime
import json
import os
import pdb
import traceback
import urllib.parse

from horey.common_utils.common_utils import CommonUtils
from notification_channel_base import NotificationChannelBase
from notification import Notification

from horey.h_logger import get_logger

logger = get_logger()


class MessageDispatcherBase:
    def __init__(self):
        self.handler_mapper = {"cloudwatch_logs_metric_sns_alarm": self.cloudwatch_logs_metric_sns_alarm_message_handler,
                               "cloudwatch_metric_lambda_duration": self.handle_cloudwatch_alarm_default}

        self.notification_channels = []
        #todo: change notification_channel_files to be comma separated environ values
        #notification_channel_files = ["notification_channel_slack.py"]
        self.notification_channel_files = os.environ.get(NotificationChannelBase.NOTIFICATION_CHANNELS_ENVIRONMENT_VARIABLE).split(",")
        for notification_channel_file_name in self.notification_channel_files:
            notification_channel_class = self.load_notification_channel(notification_channel_file_name)
            notification_channel = self.init_notification_channel(notification_channel_class)
            self.notification_channels.append(notification_channel)

    @staticmethod
    def load_notification_channel(file_name):
        """
        Load notification channel class from python module.

        @param file_name:
        @return:
        """

        module_obj = CommonUtils.load_module(os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name))
        candidates = []
        for attr_name in module_obj.__dict__:
            if attr_name == "NotificationChannelBase":
                continue

            if attr_name.startswith("NotificationChannel"):
                candidate = getattr(module_obj, attr_name)
                if issubclass(candidate, NotificationChannelBase):
                    candidates.append(candidate)

        if len(candidates) != 1:
            raise RuntimeError(file_name)

        return candidates[0]

    @staticmethod
    def init_notification_channel(notification_channel_class):
        """
        Load configuration file and init notification channel with configuration file.

        @param notification_channel_class:
        @return:
        """

        configuration = CommonUtils.load_object_from_module(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                            notification_channel_class.CONFIGURATION_POLICY_FILE_NAME),
                                                            notification_channel_class.CONFIGURATION_POLICY_CLASS_NAME)
        configuration.configuration_file_full_path = configuration.CONFIGURATION_FILE_NAME
        configuration.init_from_file()

        return notification_channel_class(configuration)

    def dispatch(self, message):
        try:
            self.handler_mapper[message.type](message)
        except KeyError:
            self.default_handler(message)
        except Exception as error_inst:
            traceback_str = ''.join(traceback.format_tb(error_inst.__traceback__))
            logger.exception(f"{traceback_str}\n{repr(error_inst)}")

            try:
                text = json.dumps(message.convert_to_dict())
            except Exception as internal_exception:
                text = f"Could not convert message to dict: error: {repr(internal_exception)}, message: {str(message)}"

            notification = Notification()
            notification.type = Notification.Types.CRITICAL
            notification.header = "Unhandled message in alert_system"
            notification.text = text

            for notification_channel in self.notification_channels:
                notification_channel.notify_alert_system_error(notification)

    def default_handler(self, message):
        try:
            alarms = self.split_sns_message_to_alarms(message)
            self.handle_cloudwatch_alarm_default(alarms)
        except Exception as error_inst:
            traceback_str = ''.join(traceback.format_tb(error_inst.__traceback__))
            logger.exception(f"{traceback_str}\n{repr(error_inst)}")

            text = json.dumps(message.convert_to_dict())
            notification = Notification()
            notification.type = Notification.Types.CRITICAL
            notification.header = "Unhandled message in alert_system"
            notification.text = text

            for notification_channel in self.notification_channels:
                notification_channel.notify_alert_system_error(notification)

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
        return self._handle_cloudwatch_logs_metric_alarm(alarm)

    def _handle_cloudwatch_logs_metric_alarm(self, alarm, notification=None):
        log_group_search_url = self.generate_cloudwatch_log_search_link(alarm, alarm.alert_system_data["log_group_name"], alarm.alert_system_data["log_group_filter_pattern"])
        if notification is None:
            notification = Notification()

        if notification.text is None:
            notification.text = f'region: {alarm.region}\n' \
               f'Log group: {alarm.alert_system_data["log_group_name"]}\n' \
               f'Filter pattern: {alarm.alert_system_data["log_group_filter_pattern"]}\n\n' \
               f'{alarm.new_state_reason}'

        notification.link = log_group_search_url
        notification.link_href = "View logs in cloudwatch"

        self._handle_cloudwatch_alarm(alarm, notification=notification)

    def _handle_cloudwatch_alarm(self, alarm, notification=None):
        if notification is None:
            notification = Notification()

        notification.tags = alarm.alert_system_data["tags"]
        if notification.type is None:
            if alarm.new_state == "OK":
                notification.type = Notification.Types.STABLE
                notification.header = notification.header or "Default handler: Cloudwatch alarm back to normal"
            elif alarm.new_state == "ALARM":
                notification.type = Notification.Types.CRITICAL
                notification.header = notification.header or "Default handler: Cloudwatch alarm triggered"
            else:
                notification.type = Notification.Types.CRITICAL
                notification.header = f'Unknown state: {alarm.new_state}'

        if notification.text is None:
            notification.text = f'*{alarm.sns_message["AlarmName"]}*\n' \
                         f'Region: {alarm.region}\n\n>' \
                         f'Reason: {alarm.new_state_reason}\n\n' \
                         f'Description: {alarm.sns_message["AlarmDescription"]}'

        for notification_channel in self.notification_channels:
            notification_channel.notify(notification)

    def generate_cloudwatch_log_search_link(self, alarm, log_group_name, log_group_filter_pattern, ):
        log_group_name_encoded = self.encode_to_aws_url_format(log_group_name)
        log_group_filter_pattern_encoded = self.encode_to_aws_url_format(log_group_filter_pattern)

        search_time_end = alarm.end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        search_time_start = alarm.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        log_group_search_url = f"https://{alarm.region}.console.aws.amazon.com/cloudwatch/home?region={alarm.region}#logsV2:log-groups/log-group/{log_group_name_encoded}/log-events$3Fend$3D{search_time_end}$26filterPattern$3D{log_group_filter_pattern_encoded}$26start$3D{search_time_start}"
        return log_group_search_url

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
        """
        Get channels based ob route tags

        @param message:
        @param alarm:
        @return:
        """

        try:
            slack_channels = self.router.get_slack_routes(message, alarm=alarm)
        except self.router.UnknownTag as exception_inst:
            logger.WARNING(f"{repr(exception_inst)}\n{''.join(traceback.format_tb(exception_inst.__traceback__))}")
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

