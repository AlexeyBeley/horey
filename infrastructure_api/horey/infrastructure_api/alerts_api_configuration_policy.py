"""
AWS ECS config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


class AlertsAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._sns_topic_name = None
        self._dynamodb_table_name = None
        self._event_bridge_rule_name = None
        self._lambda_role_name = None
        self._lambda_name = None
        self._horey_repo_path = None
        self._route_tags_to_slack_channels_mapping = None
        self._self_monitoring_slack_channel = None

    @property
    def self_monitoring_slack_channel(self):
        if self._self_monitoring_slack_channel is None:
            raise self.UndefinedValueError("self_monitoring_slack_channel")
        return self._self_monitoring_slack_channel

    @self_monitoring_slack_channel.setter
    def self_monitoring_slack_channel(self, value):
        self._self_monitoring_slack_channel = value

    @property
    def route_tags_to_slack_channels_mapping(self):
        if self._route_tags_to_slack_channels_mapping is None:
            raise self.UndefinedValueError("route_tags_to_slack_channels_mapping")
        return self._route_tags_to_slack_channels_mapping

    @route_tags_to_slack_channels_mapping.setter
    def route_tags_to_slack_channels_mapping(self, value):
        self._route_tags_to_slack_channels_mapping = value

    @property
    def horey_repo_path(self):
        if self._horey_repo_path is None:
            raise self.UndefinedValueError("horey_repo_path")
        return self._horey_repo_path

    @horey_repo_path.setter
    def horey_repo_path(self, value):
        self._horey_repo_path = value

    @property
    def lambda_name(self):
        if self._lambda_name is None:
            raise self.UndefinedValueError("lambda_name")
        return self._lambda_name

    @lambda_name.setter
    def lambda_name(self, value):
        self._lambda_name = value

    @property
    def lambda_role_name(self):
        if self._lambda_role_name is None:
            raise self.UndefinedValueError("lambda_role_name")
        return self._lambda_role_name

    @lambda_role_name.setter
    def lambda_role_name(self, value):
        self._lambda_role_name = value

    @property
    def event_bridge_rule_name(self):
        if self._event_bridge_rule_name is None:
            raise self.UndefinedValueError("event_bridge_rule_name")
        return self._event_bridge_rule_name

    @event_bridge_rule_name.setter
    def event_bridge_rule_name(self, value):
        self._event_bridge_rule_name = value

    @property
    def dynamodb_table_name(self):
        if self._dynamodb_table_name is None:
            raise self.UndefinedValueError("dynamodb_table_name")
        return self._dynamodb_table_name

    @dynamodb_table_name.setter
    def dynamodb_table_name(self, value):
        self._dynamodb_table_name = value

    @property
    def sns_topic_name(self):
        if self._sns_topic_name is None:
            raise self.UndefinedValueError("sns_topic_name")
        return self._sns_topic_name

    @sns_topic_name.setter
    def sns_topic_name(self, value):
        self._sns_topic_name = value

    @property
    def alert_system_lambda_log_group_name(self):
        return f"/aws/lambda/{self.lambda_name}"

    @property
    def lambda_timeout(self):
        return 300
