"""
Message being received by the Alert System Lambda.

"""
import datetime

from horey.h_logger import get_logger
from horey.alert_system.lambda_package.message_base import MessageBase
from horey.alert_system.lambda_package.notification import Notification

logger = get_logger()


class MessageSESDefault(MessageBase):
    """
    Main class.

    """

    ROUTING_TAG = "SES"

    def __init__(self, dict_src, configuration):
        """
        Try to init from dict

        :param dict_src:
        :return:
        """

        super().__init__(dict_src, configuration)
        try:
            self.message_dict = MessageBase.extract_message_dict(dict_src)
        except Exception as inst_error:
            raise MessageBase.NotAMatchError(f"Not a match {repr(inst_error)}")

        if self.message_dict.get("notificationType") == "AmazonSnsSubscriptionSucceeded":
            return

        if "mail" not in self.message_dict:
            raise MessageBase.NotAMatchError("Not a match")

    # pylint: disable = too-many-statements
    def generate_notification(self):
        """
        Generate notification from message.

        :return:
        """
        if self.message_dict.get("notificationType") == "AmazonSnsSubscriptionSucceeded":
            return self.generate_notification_amazon_sns_subscription_succeeded()
        notification = Notification()
        mail = self.message_dict.get("mail") or {}
        src_address = mail.get("source")
        dst_address = mail.get("destination")

        headers = mail.get("headers") or []
        for dict_header in headers:
            if dict_header.get("name") != "Subject":
                continue
            subject = dict_header.get("value")
            break
        else:
            subject = mail.get("commonHeaders") and mail.get("commonHeaders").get("subject")

        subj_src_dst = f"Subject: {subject}, Source: {src_address}, Destination {dst_address}"
        subj_src_dst_nl = f"Subject: {subject}\nSource: {src_address}\nDestination {dst_address}"
        time_string = None

        end_time = None
        start_time = None
        try:
            time_string = f'Alarm Time: {self._dict_src["Records"][0]["Sns"]["Timestamp"]}'
            end_time = datetime.datetime.strptime(
                self._dict_src["Records"][0]["Sns"]["Timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z"
            )
            start_time = end_time - datetime.timedelta(minutes=5)
            end_time += datetime.timedelta(minutes=1)
        except Exception as inst_error:
            logger.info(repr(inst_error))

        if not time_string:
            time_string = f'Email Time: {mail.get("timestamp")}'

        time_src_dst = f"{time_string}, {subj_src_dst}"
        time_src_dst_nl = f"{time_string}\n{subj_src_dst_nl}"

        try:
            region = mail.get("sourceArn").split(":")[3]
        except Exception as error_inst:
            region = repr(error_inst)

        message_id = mail.get("messageId")

        event_type = self.message_dict.get("notificationType") or self.message_dict.get("eventType")
        if not event_type:
            notification.type = Notification.Types.CRITICAL
            data = self._dict_src or self.message_dict
            notification.text = f"Was not able to find delivery type: {data}"
            email_status = "Missing both 'notificationType' and 'eventType'"
        elif event_type == "Delivery":
            notification.type = Notification.Types.DEBUG
            notification.text = f"Delivery. Region: {region}. {time_src_dst}."
            email_status = "Delivery"
        elif event_type == "DeliveryDelay":
            notification.type = Notification.Types.WARNING
            info = self.message_dict.get("deliveryDelay")
            notification.text = f"DeliveryDelay. Region: {region}. {time_src_dst}. messageId: {message_id}. Info: {info}"
            email_status = "DeliveryDelay"
        elif event_type == "Bounce":
            if self.configuration.do_not_send_ses_suppressed_bounce_notifications:
                notification.type = Notification.Types.DEBUG
                notification.text = f"Region: {region}, " \
                                    f"{time_src_dst_nl}, " \
                                    f"MessageId: {message_id}"
            else:
                notification.type = Notification.Types.WARNING
                notification.text = f"Region: {region}\n" \
                                    f"{time_src_dst_nl}\n" \
                                    f"MessageId: {message_id}\n"
            email_status = "Bounce"
        elif event_type == "Send":
            notification.type = Notification.Types.DEBUG
            notification.text = f"SES_event_Send. Region: {region}. {time_src_dst}. messageId: {message_id}."
            email_status = "Send"
        elif event_type == "Open":
            notification.type = Notification.Types.DEBUG
            notification.text = f"SES_event_Open. Region: {region}. {time_src_dst}. messageId: {message_id}."
            email_status = "Open"
        elif event_type == "Click":
            notification.type = Notification.Types.DEBUG
            notification.text = f"SES_event_Click. Region: {region}. {time_src_dst}. messageId: {message_id}."
            email_status = "Click"
        else:
            notification.type = Notification.Types.CRITICAL
            notification.text = f"Event Type: {event_type}. Event: {self._dict_src}"
            email_status = "ALERT_SYSTEM_ERROR"
        notification.header = (
                notification.header or f"SES {email_status}"
        )

        notification.link = self.generate_cloudwatch_log_search_link(
            self.configuration.alert_system_lambda_log_group_name,
            message_id,
            start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            )
        notification.link_href = "View Cloudwatch Logs"
        notification.routing_tags = [self.ROUTING_TAG]
        return notification

    def generate_notification_amazon_sns_subscription_succeeded(self):
        """
        Unique message - subscription.

        :return:
        """

        notification = Notification()
        timestamp = self._dict_src["Records"][0]["Sns"]["Timestamp"]
        notification.text = f"Timestamp: {timestamp}. " + self.message_dict.get("message")
        notification.type = Notification.Types.PARTY
        notification.header = "Amazon Sns Subscription Succeeded to SES events"
        return notification
