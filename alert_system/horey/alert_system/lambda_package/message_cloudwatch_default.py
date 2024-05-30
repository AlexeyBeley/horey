"""
Message being received by the Alert System Lambda.

"""
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
        self.message_dict = MessageBase.extract_message_dict(dict_src)
        if "AlarmArn" not in self.message_dict:
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
        breakpoint()
        notification = Notification()
        mail = self.message_dict.get("mail") or {}
        timestamp = mail.get("timestamp") or "None"
        breakpoint()
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
