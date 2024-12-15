"""
Message being received by the Alert System Lambda.

"""
import json
import urllib.parse

from horey.h_logger import get_logger
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy

logger = get_logger()


class MessageBase:
    """
    Main class.

    """

    def __init__(self, dic_src, configuration: AlertSystemConfigurationPolicy):
        self._dict_src = dic_src
        self.configuration = configuration

    @staticmethod
    def extract_message_dict(dict_src):
        """
        Extract the dictionary

        :param dict_src:
        :return:
        """

        if "Records" in dict_src:
            if list(dict_src) != ["Records"]:
                raise ValueError(f"Records is not the single field: {dict_src}")
            if len(dict_src["Records"]) != 1:
                raise ValueError(f"Records len is not 1: {dict_src}")
            for dict_record in dict_src["Records"]:
                if "EventSource" not in dict_record:
                    raise ValueError(f"EventSource is not in Record: {dict_src}")
                if dict_record["EventSource"] != "aws:sns":
                    raise ValueError(f"EventSource is not 'aws:sns:' {dict_src}")
                if "Sns" not in dict_record:
                    raise ValueError(f"Sns is not in Record: {dict_src}")
                sns_record = dict_record["Sns"]
                str_sns_message = sns_record["Message"]
                dict_sns_message = json.loads(str_sns_message)
                return dict_sns_message

        if dict_src.get("source") == "aws.cloudwatch":
            return dict_src["alarmData"]

        return dict_src

    def generate_notification(self):
        """
        Generate relevant notification.
        Will be implemented per message

        :return:
        """
        raise NotImplementedError("Implemented in class children.")

    class NotAMatchError(ValueError):
        """
        Source dictionary can not be used to initialize the required class.
        """

    def convert_to_dict(self):
        """
        Convert the message to dict.

        @return:
        """

        if self._dict_src:
            return self._dict_src

        return {
            key[1:]: value
            for key, value in self.__dict__.items()
            if key.startswith("_")
        }

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
        self, log_group_name, search_text, search_time_start, search_time_end,
    ):
        """
        Generate comfort link to relevant search in the cloudwatch logs service.

        @param log_group_name:
        @param search_text:
        @return:
        :param search_time_end:
        :param search_time_start:
        """

        log_group_name_encoded = self.encode_to_aws_url_format(log_group_name)
        search_text_encoded = self.encode_to_aws_url_format(
            search_text
        )

        log_group_search_url = (
            f"https://{self.configuration.region}.console.aws.amazon.com/cloudwatch/home?region="
            f"{self.configuration.region}#logsV2:log-groups/log-group/{log_group_name_encoded}/log-events$3Fend$3D{search_time_end}$26filterPattern$3D{search_text_encoded}$26start$3D{search_time_start}"
        )
        return log_group_search_url

    def generate_cooldown_trigger_name_and_epoch_timestamp(self):
        """
        Implemented per message class when cool down is needed.

        :return:
        """

        raise self.NoCooldown("Implement per class")

    class NoCooldown(RuntimeError):
        """
        Do not cooldown the alarm
        """
