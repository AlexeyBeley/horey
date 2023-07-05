"""
Cloud watch specific log group representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.aws_services_entities.cloud_watch_log_stream import (
    CloudWatchLogStream,
)


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
        self.arn = None
        self.retention_in_days = None

        super().__init__(dict_src, from_cache=from_cache)

        if from_cache:
            self._init_cloud_watch_log_group_from_cache(dict_src)
            return

        init_options = {
            "logGroupName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
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

    def generate_create_request(self):
        """
        Standard.

        :return:
        """

        ret = {"logGroupName": self.name, "tags": self.tags}

        return ret

    def update_from_raw_response(self, dict_src):
        """
        Standard.

        :param dict_src:
        :return:
        """

        init_options = {
            "logGroupName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "creationTime": self.init_default_attr,
            "metricFilterCount": self.init_default_attr,
            "arn": self.init_default_attr,
            "storedBytes": self.init_default_attr,
            "retentionInDays": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def update_log_stream(self, dict_src, from_cache=False):
        """
        When needed full information the stream is updated from AWS.
        :param dict_src:
        :param from_cache:
        :return:
        """
        ls = CloudWatchLogStream(dict_src, from_cache=from_cache)
        self.log_streams.append(ls)

    def generate_dir_name(self):
        """
        Generate dir name from self name.

        :return:
        """

        return self.name.lower().replace("/", "_")
