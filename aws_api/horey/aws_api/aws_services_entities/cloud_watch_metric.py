"""
Cloud watch specific log group representation
"""
import sys
import os
from horey.common_utils.common_utils import CommonUtils

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class CloudWatchMetric(AwsObject):
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
            self._init_cloud_watch_metric_from_cache(dict_src)
            return

        init_options = {
            "Namespace": self.init_default_attr,
            "MetricName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "Dimensions": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def _init_cloud_watch_metric_from_cache(self, dict_src):
        """
        Init The object from conservation.
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)
