"""
Cloud watch Metric
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class CloudWatchMetric(AwsObject):
    """
    The class to represent instances of the cloudwatch metric objects.
    """

    def __init__(self, dict_src, from_cache=False):
        """
        Init with boto3 dict

        :param dict_src:
        """

        self._dict_dimensions = None
        self.dimensions = []

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

    @property
    def dict_dimensions(self):
        """
        Formatted in a dict for ease of comparison.

        :return:
        """

        if self._dict_dimensions is None:
            self._dict_dimensions = {dimension["Name"]: dimension["Value"] for dimension in self.dimensions}
        return self._dict_dimensions

    def _init_cloud_watch_metric_from_cache(self, dict_src):
        """
        Init The object from conservation.
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)
