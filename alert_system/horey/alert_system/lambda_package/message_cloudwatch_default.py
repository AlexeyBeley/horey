"""
Message being received by the Alert System Lambda.

"""
import json
import urllib.parse

from horey.h_logger import get_logger
from horey.alert_system.lambda_package.message_base import MessageBase
from horey.alert_system.lambda_package.notification import Notification


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
        alarm_dict = MessageBase.extract_message_dict(self._dict_src)
        if "AlarmDescription" not in alarm_dict:
            raise MessageBase.NotAMatchError("Not a match")

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

    def generate_notification(self):
        """
        Generate notification from message.

        :return:
        """

        message_dict = MessageBase.extract_message_dict(self._dict_src)
        if "AlarmDescription" not in message_dict:
            raise MessageBase.NotAMatchError("AlarmDescription missing")
        alarm_description = json.loads(message_dict["AlarmDescription"])
        if MessageBase.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY in alarm_description:
            return self.generate_self_monitoring_notification(message_dict)

        breakpoint()
        if "log_group_name" in message_dict:
            breakpoint()

        log_group_search_url = self.generate_cloudwatch_log_search_link(
            message_dict,
            message_dict["log_group_name"],
            message_dict["log_group_filter_pattern"],
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
        try:
            region = mail.get("sourceArn").split(":")[3]
        except Exception as error_inst:
            region = repr(error_inst)
        try:
            message_id = mail.get("messageId")
        except Exception as error_inst:
            message_id = repr(error_inst)
        try:
            destination = mail.get("destination")
        except Exception as error_inst:
            destination = repr(error_inst)

        event_type = self.message_dict.get("notificationType") or self.message_dict.get("eventType")
        if not event_type:
            notification.type = Notification.Types.CRITICAL
            data = self._dict_src or self.message_dict
            notification.text = f"Was not able to find delivery type: {data}"
            email_status = "Missing both 'notificationType' and 'eventType'"
        elif event_type == "Delivery":
            notification.type = Notification.Types.STABLE
            notification.text = f"Delivery. Region: {region}. Timestamp: {timestamp}."
            email_status = "Delivery"
        elif event_type == "DeliveryDelay":
            notification.type = Notification.Types.WARNING
            info = self.message_dict.get("deliveryDelay") or destination
            notification.text = f"DeliveryDelay. Region: {region}. Timestamp: {timestamp}. messageId: {message_id}. Info: {info}"
            email_status = "DeliveryDelay"
        elif event_type == "Bounce":
            notification.type = Notification.Types.WARNING
            info = self.message_dict.get("bounce") or destination
            notification.text = f"DeliveryDelay. Region: {region}. Timestamp: {timestamp}. messageId: {message_id}. Info: {info}"
            email_status = "DeliveryDelay"
        elif event_type == "Send":
            notification.type = Notification.Types.INFO
            notification.text = f"DeliveryDelay. Region: {region}. Timestamp: {timestamp}. messageId: {message_id}. Destination: {destination}"
            email_status = "DeliveryDelay"
        else:
            notification.type = Notification.Types.CRITICAL
            notification.text = f"Event Type: {event_type}. Event: {self._dict_src}"
            email_status = "ALERT_SYSTEM_ERROR"
        notification.header = (
                notification.header or f"Default SES handler: {email_status}"
        )

        return notification

    def generate_self_monitoring_notification(self, message_dict):
        """
        All cloud watch self monitoring metrics handled here

        :param message_dict:
        :return:
        """

        notification = Notification()
        alarm_description = json.loads(message_dict["AlarmDescription"])

        notification.tags = alarm_description["routing_tags"]
        notification.header = "Alert System self monitoring"
        alarm_name = message_dict["AlarmName"]
        region_mark = message_dict["AlarmArn"].split(":")[2]
        notification.link = f"https://{region_mark}.console.aws.amazon.com/cloudwatch/home?region={region_mark}#alarmsV2:alarm/{alarm_name}"

        if message_dict["NewStateValue"] == "OK":
            notification.type = Notification.Types.STABLE
        else:
            notification.type = Notification.Types.CRITICAL

        if "log_group_name" in alarm_description and "log_group_filter_pattern" in alarm_description:
            pattern = alarm_description.get("log_group_filter_pattern")
            pattern_middle = int(len(pattern)//2)
            pattern = pattern[:pattern_middle] + "_horey_explicit_split_" + pattern[pattern_middle:]
            log_group_name = alarm_description.get("log_group_name")
            reason = f"Pattern '{pattern}' found in Lambda log group: {log_group_name}"
            lambda_name = message_dict["Trigger"]["Namespace"].split("/")[-1]
        elif message_dict["Trigger"]["MetricName"] == "Duration":
            # alarm.threshold = self.configuration.lambda_timeout * 0.6 * 1000
            threshold_sec = int(message_dict["Trigger"]["Threshold"] // 1000)
            reason = f"Lambda duration > {threshold_sec} seconds"
            name_dimensions = list(filter(lambda x: x["name"] == "FunctionName", message_dict["Trigger"]["Dimensions"]))
            if len(name_dimensions) != 1:
                raise RuntimeError(name_dimensions)
            lambda_name = name_dimensions[0]["value"]
        elif message_dict["Trigger"]["MetricName"] == "Errors":
            # alarm.threshold = self.configuration.lambda_timeout * 0.6 * 1000
            threshold_sec = int(message_dict["Trigger"]["Threshold"] // 1000)
            reason = f"Lambda finished with errors in last {threshold_sec} seconds"
            name_dimensions = list(filter(lambda x: x["name"] == "FunctionName", message_dict["Trigger"]["Dimensions"]))
            if len(name_dimensions) != 1:
                raise RuntimeError(name_dimensions)
            lambda_name = name_dimensions[0]["value"]
        else:
            raise NotImplementedError(f'{message_dict["Trigger"]["MetricName"]=}')

        alarm_time = message_dict["StateChangeTime"]
        new_state_reason = message_dict["NewStateReason"]
        notification.text = (
            f"Region: {region_mark}\n"
            f'Lambda Name: {lambda_name}\n'
            f'HR Reason: {reason}\n'
            f'Raw reason: \'{new_state_reason}\'\n'
            f'Time: {alarm_time}\n'
        )

        return notification

    def generate_alert_description(self):
        """
        Generate string to be used by description.

        :return:
        """

        return json.dumps(self.message_dict)
