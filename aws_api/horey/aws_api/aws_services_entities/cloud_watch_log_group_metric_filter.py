"""
Cloud watch log group metric
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class CloudWatchLogGroupMetricFilter(AwsObject):
    """
    The class to represent Cloud watch log group metric
    """

    def __init__(self, dict_src, from_cache=False):
        """
        Init with boto3 dict
        :param dict_src:
        """

        self.log_streams = []
        self.filter_pattern = None
        self.log_group_name = None
        self.metric_transformations = None

        super().__init__(dict_src, from_cache=from_cache)

        if from_cache:
            self._init_cloud_watch_log_group_from_cache(dict_src)
            return

        init_options = {
            "filterName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "metricTransformations": self.init_default_attr,
            "creationTime": self.init_default_attr,
            "logGroupName": self.init_default_attr,
            "filterPattern": self.init_default_attr,
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

    def generate_dir_name(self):
        """
        Looks like copy/past error from cloudwatch log group

        return self.name.lower().replace("/", "_")
        :return:
        """

        raise NotImplementedError()

    def generate_create_request(self):
        """
        [REQUIRED]
        logGroupName (string) --
        filterName (string) --
        filterPattern (string) --
        metricTransformations (list) --
        metricName (string) --
        metricNamespace (string) --
        metricValue (string) --
        """
        request_dict = {
            "logGroupName": self.log_group_name,
            "filterName": self.name,
            "filterPattern": self.filter_pattern,
            "metricTransformations": self.metric_transformations,
        }
        return request_dict
