"""
Cloud watch Alarm
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


# pylint: disable= too-many-instance-attributes
class CloudWatchAlarm(AwsObject):
    """
    The class to represent instances of the Cloudwatch alarm
    """

    def __init__(self, dict_src, from_cache=False):
        """
        Init with boto3 dict
        :param dict_src:
        """

        self.log_streams = []
        self.alarm_description = None
        self.insufficient_data_actions = None
        self.dimensions = []
        self.ok_actions = None
        self.unit = None
        self.actions_enabled = None
        self.alarm_actions = None
        self.metric_name = None
        self.namespace = None
        self.statistic = None
        self.period = None
        self.evaluation_periods = None
        self.datapoints_to_alarm = None
        self.threshold = None
        self.comparison_operator = None
        self.treat_missing_data = None
        self._dict_dimensions = None

        super().__init__(dict_src, from_cache=from_cache)

        if from_cache:
            self._init_cloud_watch_alarm_from_cache(dict_src)
            return

        init_options = {
            "AlarmName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "AlarmArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "AlarmConfigurationUpdatedTimestamp": self.init_default_attr,
            "ActionsEnabled": self.init_default_attr,
            "OKActions": self.init_default_attr,
            "AlarmActions": self.init_default_attr,
            "InsufficientDataActions": self.init_default_attr,
            "StateValue": self.init_default_attr,
            "StateReason": self.init_default_attr,
            "StateReasonData": self.init_default_attr,
            "StateUpdatedTimestamp": self.init_default_attr,
            "Namespace": self.init_default_attr,
            "Statistic": self.init_default_attr,
            "Dimensions": self.init_default_attr,
            "Period": self.init_default_attr,
            "EvaluationPeriods": self.init_default_attr,
            "DatapointsToAlarm": self.init_default_attr,
            "Threshold": self.init_default_attr,
            "ComparisonOperator": self.init_default_attr,
            "TreatMissingData": self.init_default_attr,
            "AlarmDescription": self.init_default_attr,
            "MetricName": self.init_default_attr,
            "StateTransitionedTimestamp": self.init_default_attr,
            "Unit": self.init_default_attr,
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

    def _init_cloud_watch_alarm_from_cache(self, dict_src):
        """
        Init The object from conservation.
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def generate_create_request(self):
        """
        [REQUIRED]
        AlarmName (string) --
        EvaluationPeriods (string) --
        """
        request_dict = {
            "AlarmName": self.name,
            "ActionsEnabled": self.actions_enabled,
            "AlarmActions": self.alarm_actions,
            "MetricName": self.metric_name,
            "Namespace": self.namespace,
            "Statistic": self.statistic,
            "Period": self.period,
            "EvaluationPeriods": self.evaluation_periods,
            "DatapointsToAlarm": self.datapoints_to_alarm,
            "Threshold": self.threshold,
            "ComparisonOperator": self.comparison_operator,
            "TreatMissingData": self.treat_missing_data,
        }

        if self.ok_actions is not None:
            request_dict["OKActions"] = self.ok_actions

        if self.dimensions is not None:
            request_dict["Dimensions"] = self.dimensions

        if self.insufficient_data_actions is not None:
            request_dict["InsufficientDataActions"] = self.insufficient_data_actions

        if self.alarm_description is not None:
            request_dict["AlarmDescription"] = self.alarm_description

        if self.unit is not None:
            request_dict["Unit"] = self.unit

        return request_dict
