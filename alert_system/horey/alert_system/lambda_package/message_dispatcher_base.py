"""
Module handling most of the basic message behavior.
Check message type - invoke relevant handler.
Send the notification to the channels.

"""

import datetime
import json
import os
import traceback
import urllib.parse

from notification_channel_base import NotificationChannelBase
from notification import Notification

from horey.common_utils.common_utils import CommonUtils
from horey.h_logger import get_logger

logger = get_logger()


class MessageDispatcherBase:
    """
    Main class.

    """

    def __init__(self):
        self.handler_mapper = {
            "cloudwatch_logs_metric_sns_alarm": self.cloudwatch_logs_metric_sns_alarm_message_handler,
            "cloudwatch_sqs_visible_alarm": self.cloudwatch_sqs_visible_alarm_message_handler,
            "cloudwatch_metric_lambda_duration": self.handle_cloudwatch_message_default,
            "cloudwatch_default": self.handle_cloudwatch_message_default,
            "ses_default": self.handle_ses_message_default,
            "sns_raw": self.handle_sns_raw_message,
        }

        self.notification_channels = []
        self.notification_channel_files = os.environ.get(
            NotificationChannelBase.NOTIFICATION_CHANNELS_ENVIRONMENT_VARIABLE
        ).split(",")
        for notification_channel_file_name in self.notification_channel_files:
            notification_channel_class = self.load_notification_channel(
                notification_channel_file_name
            )
            notification_channel = self.init_notification_channel(
                notification_channel_class
            )
            self.notification_channels.append(notification_channel)

    @staticmethod
    def load_notification_channel(file_name):
        """
        Load notification channel class from python module.

        @param file_name:
        @return:
        """

        module_obj = CommonUtils.load_module(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
        )
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

        configuration = CommonUtils.load_object_from_module(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                notification_channel_class.CONFIGURATION_POLICY_FILE_NAME,
            ),
            notification_channel_class.CONFIGURATION_POLICY_CLASS_NAME,
        )
        configuration.configuration_file_full_path = (
            configuration.CONFIGURATION_FILE_NAME
        )
        configuration.init_from_file()

        return notification_channel_class(configuration)

    def dispatch(self, message):
        """
        Dispatch message - try to use mapped functions.
        If failed use default cloudwatch handler.
        If failed - notify alert_system_monitoring authority. CRITICAL

        @param message:
        @return:
        """

        try:
            return self.handler_mapper[message.type](message)
        except Exception as error_inst:
            traceback_str = "".join(traceback.format_tb(error_inst.__traceback__))
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
        return None

    def handle_cloudwatch_message_default(self, message, notify_on_failure=True):
        """
        Standard cloudwatch message handling.

        @param notify_on_failure:
        @param message:
        @return:
        """

        try:
            alarms = self.split_sns_message_to_alarms(message)
            self.handle_cloudwatch_alarms_default(alarms)
        except Exception as error_inst:
            if not notify_on_failure:
                return

            traceback_str = "".join(traceback.format_tb(error_inst.__traceback__))
            logger.exception(f"{traceback_str}\n{repr(error_inst)}")

            text = json.dumps(message.convert_to_dict())
            notification = Notification()
            notification.type = Notification.Types.CRITICAL
            notification.header = "Unhandled message in alert_system"
            notification.text = text

            for notification_channel in self.notification_channels:
                notification_channel.notify_alert_system_error(notification)

    def handle_cloudwatch_alarms_default(self, alarms):
        """
        Standard cloudwatch alarms handling.

        @param alarms:
        @return:
        """

        for alarm in alarms:
            self._handle_cloudwatch_alarm(alarm)

    @staticmethod
    def split_sns_message_to_alarms(message):
        """
        Split message records to CloudwatchAlarm objects.

        @param message:
        @return:
        """

        return [
            CloudwatchAlarm(record_dict) for record_dict in message.dict_src["Records"]
        ]

    def cloudwatch_logs_metric_sns_alarm_message_handler(self, message):
        """
        Alarm received via SNS channel from cloudwatch.

        @param message:
        @return:
        """

        alarms = self.split_sns_message_to_alarms(message)
        for alarm in alarms:
            self.handle_cloudwatch_logs_metric_alarm(alarm)

    def handle_cloudwatch_logs_metric_alarm(self, alarm):
        """
        Common scenario - found some string and notified SNS topic.

        @param alarm:
        @return:
        """

        return self._handle_cloudwatch_logs_metric_alarm(alarm)

    def _handle_cloudwatch_logs_metric_alarm(self, alarm, notification=None):
        """
        Helper function to give the user ability to customize the notification appearance.

        @param alarm:
        @return:
        """

        log_group_search_url = self.generate_cloudwatch_log_search_link(
            alarm,
            alarm.alert_system_data["log_group_name"],
            alarm.alert_system_data["log_group_filter_pattern"],
        )
        if notification is None:
            notification = Notification()

        if notification.text is None:
            notification.text = (
                f"region: {alarm.region}\n"
                f'Log group: {alarm.alert_system_data["log_group_name"]}\n'
                f'Filter pattern: {alarm.alert_system_data["log_group_filter_pattern"]}\n\n'
                f"{alarm.new_state_reason}"
            )

        notification.link = log_group_search_url
        notification.link_href = "View logs in cloudwatch"

        self._handle_cloudwatch_alarm(alarm, notification=notification)

    def cloudwatch_sqs_visible_alarm_message_handler(self, message):
        """
        Common scenario - cloudwatch notified SNS topic on SQS visible messages count.

        @param message:
        @return:
        """

        alarms = self.split_sns_message_to_alarms(message)
        for alarm in alarms:
            self.handle_cloudwatch_sqs_visible_alarm(alarm)

    def handle_cloudwatch_sqs_visible_alarm(self, alarm):
        """
        Handle each alarm in the message.

        @param alarm:
        @return:
        """

        return self._handle_cloudwatch_sqs_visible_alarm(alarm)

    def _handle_cloudwatch_sqs_visible_alarm(self, alarm, notification=None):
        """
        Helper function to give the user ability to customize the notification appearance.

        @param alarm:
        @return:
        """
        if notification is None:
            notification = Notification()

        if notification.text is None:
            notification.text = (
                f"region: {alarm.region}\n"
                f'Queue name: {alarm.alert_system_data["queue_name"]}\n'
                f"{alarm.new_state_reason}"
            )

        self._handle_cloudwatch_alarm(alarm, notification=notification)

    def _handle_cloudwatch_alarm(self, alarm, notification=None):
        """
        Handle generic cloudwatch alarm. Not to smart function, used as a default formatter,
        so new cloudwatch alarms will have at least basic formatting.

        @param alarm:
        @param notification:
        @return:
        """

        if notification is None:
            notification = Notification()

        notification.tags = alarm.routing_tags

        if notification.type is None:
            if alarm.new_state == "OK":
                notification.type = Notification.Types.STABLE
                notification.header = (
                    notification.header
                    or "Default handler: Cloudwatch alarm back to normal"
                )
            elif alarm.new_state == "ALARM":
                notification.type = Notification.Types.CRITICAL
                notification.header = (
                    notification.header or "Default handler: Cloudwatch alarm triggered"
                )
            else:
                notification.type = Notification.Types.CRITICAL
                notification.header = f"Unknown state: {alarm.new_state}"

        if notification.text is None:
            notification.text = (
                f'*{alarm.sns_message["AlarmName"]}*\n'
                f"Region: {alarm.region}\n\n>"
                f"Reason: {alarm.new_state_reason}\n\n"
                f'Description: {alarm.sns_message["AlarmDescription"]}'
            )

        for notification_channel in self.notification_channels:
            notification_channel.notify(notification)

    def generate_cloudwatch_log_search_link(
        self, alarm, log_group_name, log_group_filter_pattern
    ):
        """
        Generate comfort link to relevant search in the cloudwatch logs service.

        @param alarm:
        @param log_group_name:
        @param log_group_filter_pattern:
        @return:
        """

        log_group_name_encoded = self.encode_to_aws_url_format(log_group_name)
        log_group_filter_pattern_encoded = self.encode_to_aws_url_format(
            log_group_filter_pattern
        )

        search_time_end = alarm.end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        search_time_start = alarm.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        log_group_search_url = (
            f"https://{alarm.region}.console.aws.amazon.com/cloudwatch/home?region="
            f"{alarm.region}#logsV2:log-groups/log-group/{log_group_name_encoded}/log-events$3Fend$3D{search_time_end}$26filterPattern$3D{log_group_filter_pattern_encoded}$26start$3D{search_time_start}"
        )
        return log_group_search_url

    @staticmethod
    def encode_to_aws_url_format(str_src):
        """
        AWS uses nonstandard url formatting.
        All special characters like '/' and '"' must be encoded.

        Sample:
        https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Fecs$252Fcontainer-name/log-events$3FfilterPattern$3D$2522$255BINFO$255D$2522

        @param str_src:
        @return:
        """

        ret = urllib.parse.quote(str_src, safe="")
        return ret.replace("%", "$25")

    def handle_ses_message_default(self, message):
        """
        Standard AWS SES message handling.

        @param message:
        @return:
        """

        bounce = None
        try:
            bounce = message.bounce
        except AttributeError:
            pass

        mail = None
        try:
            mail = message.mail
        except AttributeError:
            pass

        self.handle_ses_message_bounce(bounce, mail)

    def handle_ses_message_bounce(self, bounce, mail):
        """
        Handle bounce messages.
        https://eu-central-1.console.aws.amazon.com/ses/home?region=eu-central-1#/suppression-list

        @param bounce:
        @param mail:
        @return:
        """

        notification = Notification()

        notification.type = Notification.Types.CRITICAL
        notification.header = (
            notification.header or "Default SES handler: Bounce received"
        )
        try:
            region = mail["sourceArn"].split(":")[3]
        except Exception:
            region = "Unknown"

        notification.text = (
            f"*Email Bounce*\n"
            f"Region: {region}\n\n>"
            f'bounceType: {bounce["bounceType"]}\n\n'
            f'bounceSubType: {bounce["bounceSubType"]}\n\n'
            f'bouncedRecipients: {bounce["bouncedRecipients"]}\n\n'
            f'headers: mail["headers"]\n\n'
        )

        for notification_channel in self.notification_channels:
            notification.tags = [
                notification_channel.configuration.ALERT_SYSTEM_MONITORING_ROUTING_TAG
            ]
            notification_channel.notify(notification)

    def handle_sns_raw_message(self, message):
        """
        Handle raw message. Send the data.

        :param message:
        :return:
        """

        notification = Notification()

        message_type = message.data.get("type")
        message_type = Notification.Types.__members__[message_type] if message_type in Notification.Types.__members__ else Notification.Types.CRITICAL
        notification.type = message_type

        notification.header = message.data.get("header") or "Default 'header'"
        notification.text = message.data.get("text") or "Default 'text'"

        for notification_channel in self.notification_channels:
            notification.tags = message.data.get("tags") or [notification_channel.configuration.ALERT_SYSTEM_MONITORING_ROUTING_TAG]
            notification_channel.notify(notification)

        return notification


class CloudwatchAlarm:
    """
    Object representing a standard cloudwatch alarm sent via SNS;

    """

    def __init__(self, dict_src):
        self.dict_src = dict_src
        self._sns_message = None
        self._alert_system_data = None
        self._start_time = None
        self._end_time = None

    @property
    def sns_message(self):
        """
        Internal message in the received dictionary.

        @return:
        """

        if self._sns_message is None:
            self._sns_message = json.loads(self.dict_src["Sns"]["Message"])
        return self._sns_message

    @property
    def region(self):
        """
        Region the alarm was sent in.

        @return:
        """

        return self.sns_message["AlarmArn"].split(":")[3]

    @property
    def alert_system_data(self):
        """
        Explicitly set message in the description field.

        @return:
        """

        if self._alert_system_data is None:
            self._alert_system_data = json.loads(
                self.sns_message["AlarmDescription"]
            ).get("data")
        return self._alert_system_data

    @property
    def routing_tags(self):
        """
        Get the routing tags if exist.

        @return:
        """
        if self.alert_system_data is not None:
            return self.alert_system_data["tags"]
        return None

    @property
    def start_time(self):
        """
        Alarm calculations start time
        2022-07-14T16:14:03.407+0000

        @return:
        """
        if self._start_time is None:
            self._start_time = self.end_time - datetime.timedelta(
                seconds=self.sns_message["Trigger"]["Period"]
            )
        return self._start_time

    @property
    def end_time(self):
        """
        Alarm calculations end time

        @return:
        """

        if self._end_time is None:
            self._end_time = datetime.datetime.strptime(
                self.sns_message["StateChangeTime"], "%Y-%m-%dT%H:%M:%S.%f%z"
            )
        return self._end_time

    @property
    def new_state(self):
        """
        New state reported by the alarm.

        @return:
        """

        return self.sns_message["NewStateValue"]

    @property
    def new_state_reason(self):
        """
        New state reason reported by the alarm.

        @return:
        """

        return self.sns_message["NewStateReason"]
