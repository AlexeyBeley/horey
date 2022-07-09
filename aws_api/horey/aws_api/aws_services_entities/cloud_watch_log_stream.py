from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.common_utils.common_utils import CommonUtils


class CloudWatchLogStream(AwsObject):
    """
    The class representing log group's log stream
    """

    def __init__(self, dict_src, from_cache=False):
        self.statements = []

        super(CloudWatchLogStream, self).__init__(dict_src, from_cache=from_cache)

        if from_cache:
            self.init_log_stream_from_cache(dict_src)
            return

        init_options = {"logStreamName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
                        "creationTime": lambda name, value: (name, CommonUtils.timestamp_to_datetime(value / 1000.0)),
                        "firstEventTimestamp": self.init_default_attr,
                        "lastEventTimestamp": self.init_default_attr,
                        "lastIngestionTime": self.init_default_attr,
                        "uploadSequenceToken": self.init_default_attr,
                        "arn": self.init_default_attr,
                        "storedBytes": self.init_default_attr
                        }

        self.init_attrs(dict_src, init_options)

    def init_log_stream_from_cache(self, dict_src):
        """
        Init the logstream from a preserved cache dict.
        :param dict_src:
        :return:
        """
        options = {}

        self._init_from_cache(dict_src, options)