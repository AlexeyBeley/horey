"""
Cloud watch specific log group representation
"""
import sys
import os
from common_utils import CommonUtils
sys.path.insert(0, os.path.join(os.path.abspath("../.."), "IP", "ip", "src"))

from aws_object import AwsObject


class CloudWatchLogGroup(AwsObject):
    """
    The class to represent instances of the log group objects.
    """
    def __init__(self, dict_src, from_cache=False):
        """
        Init with boto3 dict
        :param dict_src:
        """

        self.log_streams = []

        super().__init__(dict_src, from_cache=from_cache)

        if from_cache:
            self._init_cloud_watch_log_group_from_cache(dict_src)
            return

        init_options = {
                        "logGroupName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
                        "creationTime": self.init_default_attr,
                        "metricFilterCount": self.init_default_attr,
                        "arn": self.init_default_attr,
                        "storedBytes": self.init_default_attr,
                        "retentionInDays": self.init_default_attr,
                        }

        self.init_attrs(dict_src, init_options)

    def _init_cloud_watch_log_group_from_cache(self, dict_src):
        """
        Init The object from conservation.
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def update_log_stream(self, dict_src, from_cache=False):
        """
        When needed full information the stream is updated from AWS.
        :param dict_src:
        :param from_cache:
        :return:
        """
        ls = CloudWatchLogGroup.LogStream(dict_src, from_cache=from_cache)
        self.log_streams.append(ls)

    class LogStream(AwsObject):
        """
        The class representing log group's log stream
        """
        def __init__(self, dict_src, from_cache=False):
            self.statements = []

            super(CloudWatchLogGroup.LogStream, self).__init__(dict_src, from_cache=from_cache)

            if from_cache:
                self.init_log_stream_from_cache(dict_src)
                return

            init_options = {"logStreamName":  self.init_default_attr,
                            "creationTime": lambda name, value: (name, CommonUtils.timestamp_to_datetime(value/1000.0)),
                            "firstEventTimestamp":  self.init_default_attr,
                            "lastEventTimestamp":  self.init_default_attr,
                            "lastIngestionTime":  self.init_default_attr,
                            "uploadSequenceToken":  self.init_default_attr,
                            "arn":  self.init_default_attr,
                            "storedBytes":  self.init_default_attr
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
