"""
Message being received by the Alert System Lambda.

"""
import json

from horey.h_logger import get_logger

logger = get_logger()


class MessageBase:
    """
    Main class.

    """

    def __init__(self, dic_src):
        self._dict_src = dic_src

    @staticmethod
    def extract_message_dict(dict_src):
        """
        Extract the dictionary

        :param dict_src:
        :return:
        """

        if "alert_system_message_class" in dict_src:
            return dict_src

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
        raise NotImplementedError(dict_src)

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
