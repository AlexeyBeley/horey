"""
Cloud watch specific log group representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class CloudWatchAlarm(AwsObject):
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
            self._init_cloud_watch_alarm_from_cache(dict_src)
            return

        init_options = {
            "AlarmName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
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
        }

        self.init_attrs(dict_src, init_options)

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
            "OKActions": self.ok_actions,
            "AlarmActions": self.alarm_actions,
            "InsufficientDataActions": self.insufficient_data_actions,
            "MetricName": self.metric_name,
            "Namespace": self.namespace,
            "Statistic": self.statistic,
            "Dimensions": self.dimensions,
            "Period": self.period,
            "EvaluationPeriods": self.evaluation_periods,
            "DatapointsToAlarm": self.datapoints_to_alarm,
            "Threshold": self.threshold,
            "ComparisonOperator": self.comparison_operator,
            "TreatMissingData": self.treat_missing_data,
        }
        return request_dict
