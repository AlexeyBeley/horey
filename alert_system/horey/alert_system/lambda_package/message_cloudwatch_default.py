"""
Message being received by the Alert System Lambda.

"""
import datetime
import json
import urllib.parse

from horey.h_logger import get_logger
from horey.alert_system.lambda_package.message_base import MessageBase
from horey.alert_system.lambda_package.notification import Notification
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy


logger = get_logger()


class MessageCloudwatchDefault(MessageBase):
    """
    Main class.

    """

    def __init__(self, dict_src):
        """
        Try to init from dict

        :param dict_src:
        :return:
        """

        super().__init__(dict_src)
        self._message_dict = None
        self._trigger = None
        self._region = None
        self._alarm_description = None
        self._end_time = None
        if "AlarmDescription" not in self.message_dict:
            raise MessageBase.NotAMatchError("Not a match")
        logger.info("MessageCloudwatchDefault initialized")

    @property
    def end_time(self):
        """
        Alert time.

        :return:
        """

        if self._end_time is None:
            self._end_time = datetime.datetime.strptime(
                self.message_dict["StateChangeTime"], "%Y-%m-%dT%H:%M:%S.%f%z"
            )
        return self._end_time

    @property
    def start_time(self):
        """
        Problem starting time

        :return:
        """

        return self.end_time - datetime.timedelta(seconds=self.trigger.get("Period", 600))

    @property
    def message_dict(self):
        """
        Extract and save.

        :return:
        """

        if self._message_dict is None:
            self._message_dict = MessageBase.extract_message_dict(self._dict_src)
        return self._message_dict

    @property
    def trigger(self):
        """
        Extract and save

        :return:
        """

        if self._trigger is None:
            self._trigger = self.message_dict.get("Trigger")
        return self._trigger

    @property
    def region(self):
        """
        AWS Region extracted from the message data.

        :return:
        """

        if self._region is None:
            self._region = self.message_dict["AlarmArn"].split(":")[3]
        return self._region

    @property
    def alarm_description(self):
        """
        Extract and save

        :return:
        """

        if self._alarm_description is None:
            self._alarm_description = json.loads(self.message_dict.get("AlarmDescription"))
        return self._alarm_description

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

    def generate_cloudwatch_alarm_link(self):
        """
        Generate comfort link to relevant search in the cloudwatch logs service.

        @return:
        """

        alarm_name = self.message_dict["AlarmName"].replace("/", "$2F")
        return f"https://{self.region}.console.aws.amazon.com/cloudwatch/home?region={self.region}#alarmsV2:alarm/{alarm_name}"

    def generate_alert_system_lambda_link(self):
        """
        Generate link to be used in notification.

        :return:
        """

        lambda_name = self.get_dimension("FunctionName")

        return f"https://{self.region}.console.aws.amazon.com/lambda/home?region={self.region}#/functions/{lambda_name}?tab=monitoring"

    def generate_cloudwatch_log_search_link(
        self, log_group_name, log_group_filter_pattern
    ):
        """
        Generate comfort link to relevant search in the cloudwatch logs service.

        @param log_group_name:
        @param log_group_filter_pattern:
        @return:
        """

        log_group_name_encoded = self.encode_to_aws_url_format(log_group_name)
        log_group_filter_pattern_encoded = self.encode_to_aws_url_format(
            log_group_filter_pattern
        )
        search_time_end = self.end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        search_time_start = self.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        log_group_search_url = (
            f"https://{self.region}.console.aws.amazon.com/cloudwatch/home?region="
            f"{self.region}#logsV2:log-groups/log-group/{log_group_name_encoded}/log-events$3Fend$3D{search_time_end}$26filterPattern$3D{log_group_filter_pattern_encoded}$26start$3D{search_time_start}"
        )
        return log_group_search_url

    def generate_notification(self):
        """
        Generate notification from message.

        :return:
        """

        if not self.alarm_description:
            raise MessageBase.NotAMatchError("AlarmDescription missing")

        if not self.trigger:
            raise MessageBase.NotAMatchError("Trigger is missing")

        if MessageBase.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY in self.alarm_description:
            return self.generate_self_monitoring_notification()

        if self.trigger.get("MetricName") == "Duration" and self.trigger.get("Namespace") == "AWS/Lambda":
            return self.generate_notification_lambda_duration()

        if "log_group_filter_pattern" in self.alarm_description:
            return self.generate_notification_log_group_filter_pattern()

        notification = self.generate_notification_default()

        return notification

    def get_dimension(self, name):
        """
        Find dimension value by name

        :param name:
        :return:
        """

        for dimension in self.trigger["Dimensions"]:
            if dimension.get("name") == name:
                return dimension["value"]
        return None

    def generate_notification_lambda_duration(self):
        """
        Generate lambda duration message

        :return:
        """

        threshold_sec = int(self.message_dict["Trigger"]["Threshold"] // 1000)
        reason = f"Lambda duration > {threshold_sec} seconds"
        new_state_reason = self.message_dict["NewStateReason"]
        alarm_time = self.message_dict["StateChangeTime"]
        lambda_name = self.get_dimension("FunctionName")

        notification = Notification()
        notification.type = Notification.Types.STABLE if self.message_dict["NewStateValue"] == "OK" else Notification.Types.CRITICAL
        notification.header = f"Lambda '{lambda_name}' duration error"
        notification.text = (
            f"Region: {self.region}\n"
            f'Lambda Name: {lambda_name}\n'
            f'HR Reason: {reason}\n'
            f'Raw reason: \'{new_state_reason}\'\n'
            f'Time: {alarm_time}\n'
        )

        notification.link = self.generate_alert_system_lambda_link()
        notification.link_href = "Lambda Link"
        notification.routing_tags = self.alarm_description.get("routing_tags")
        if not notification.routing_tags:
            notification.routing_tags = [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG]
        return notification

    def generate_self_monitoring_notification(self):
        """
        All cloud watch self monitoring metrics handled here

        :return:
        """

        lambda_name = self.alarm_description["lambda_name"]

        if "log_group_name" in self.alarm_description and "log_group_filter_pattern" in self.alarm_description:
            notification = self.generate_notification_log_group_filter_pattern()
        elif self.trigger["MetricName"] == "Duration":
            notification = self.generate_notification_default()
            notification.link = self.generate_alert_system_lambda_link()
            notification.link_href = "AlertSystem Lambda Link"
        elif self.trigger["MetricName"] == "Errors":
            if self.message_dict["Trigger"]["Threshold"] > 1000:
                threshold_sec = int(self.message_dict["Trigger"]["Threshold"] // 1000)
            else:
                threshold_sec = int(self.message_dict["Trigger"]["Threshold"])
            reason = f"Lambda finished with errors in last {threshold_sec} seconds"
            notification = self.generate_notification_default(reason=reason)
            notification.link = self.generate_alert_system_lambda_link()
            notification.link_href = "AlertSystem Lambda Link"
        else:
            raise NotImplementedError(f'{self.message_dict["Trigger"]["MetricName"]=}')

        if Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG not in notification.routing_tags:
            notification.routing_tags.append(Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG)

        notification.header = "Alert System Self Monitoring"
        notification.text += f"\nLambda Name: {lambda_name}"

        return notification

    def generate_notification_log_group_filter_pattern(self):
        """
        Generate notification pointing the log group.

        :return:
        """

        pattern = self.alarm_description.get("log_group_filter_pattern")
        log_group_name = self.alarm_description.get("log_group_name")
        new_state_reason = self.message_dict["NewStateReason"]
        alarm_time = self.message_dict["StateChangeTime"]

        pattern_log = pattern.replace(AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_LOG_ERROR_FILTER_PATTERN,
                                      "ALERT_SYSTEM_SELF_MONITORING_LOG_ERROR_FILTER_PATTERN")
        pattern_log = pattern_log.replace(
            AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_LOG_TIMEOUT_FILTER_PATTERN,
            "ALERT_SYSTEM_SELF_MONITORING_LOG_TIMEOUT_FILTER_PATTERN")

        logger.info(f"Found {pattern_log} in {log_group_name}")

        reason = f"Pattern '{pattern}' found in log group: {log_group_name}"

        notification = Notification()
        notification.type = Notification.Types.STABLE if self.message_dict["NewStateValue"] == "OK" else Notification.Types.CRITICAL
        notification.header = "Log filter pattern pattern found"

        notification.text = f"Region: {self.region}\n" \
                            f"Reason: {reason}\n" \
                            f"Time: {alarm_time}\n" \
                            f"Raw reason: \'{new_state_reason}\'\n'"

        notification.link = self.generate_cloudwatch_log_search_link(log_group_name, pattern)

        notification.link_href = "Log group"
        notification.routing_tags = self.alarm_description.get("routing_tags")
        if not notification.routing_tags:
            notification.routing_tags = [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG]
        return notification

    def generate_notification_default(self, reason=None):
        """
        Generate basic information notification.

        :return:
        """

        new_state_reason = self.message_dict["NewStateReason"]
        alarm_time = self.message_dict["StateChangeTime"]

        notification = Notification()
        notification.type = Notification.Types.STABLE if self.message_dict["NewStateValue"] == "OK" else Notification.Types.CRITICAL
        notification.header = f"Alarm {self.message_dict['AlarmName']}"
        reason = f"Reason: Metric {self.trigger['MetricName']}\n" if reason is None else (reason.strip("\n") + "\n")
        notification.text = (
            f"Region: {self.region}\n"
            f"Raw reason: '{new_state_reason}'\n"
            f"{reason}"
            f'Time: {alarm_time}\n'
        )

        notification.routing_tags = self.alarm_description.get("routing_tags")
        if not notification.routing_tags:
            notification.routing_tags = [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG]

        notification.link = self.generate_cloudwatch_alarm_link()
        notification.link_href = "Goto Alarm"
        return notification

    def generate_alert_description(self):
        """
        Generate string to be used by description.

        return json.dumps(self.message_dict)
        :return:
        """
        raise NotImplementedError("What is this code?")
