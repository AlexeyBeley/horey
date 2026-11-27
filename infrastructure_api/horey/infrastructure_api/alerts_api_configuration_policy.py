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
        self._routing_tags_to_slack_channels_mapping = None
        self._self_monitoring_slack_channel = None
        self._bearer_token = None
        self._ses_alert_slack_channel = None
        self._do_not_send_ses_suppressed_bounce_notifications = False
        self._postgres_cluster_identifier = None
        self._routing_tags = None
        self._sns_subscription_name = None
        self._sns_topic_name = None
        self._slug = None

    @property
    def sns_topic_name(self):
        if self._sns_topic_name is None:
            self._sns_topic_name = f"topic-{self.slug}"
        return self._sns_topic_name

    @sns_topic_name.setter
    def sns_topic_name(self, value):
        self._sns_topic_name = value

    @property
    def sns_subscription_name(self):
        if self._sns_subscription_name is None:
            self._sns_subscription_name = f"subscription-{self.slug}"
        return self._sns_subscription_name

    @sns_subscription_name.setter
    def sns_subscription_name(self, value):
        self._sns_subscription_name = value

    @property
    def routing_tags(self):
        self.check_defined()
        return self._routing_tags

    @routing_tags.setter
    def routing_tags(self, value):
        self._routing_tags = value

    @property
    def postgres_cluster_identifier(self):
        return self._postgres_cluster_identifier

    @postgres_cluster_identifier.setter
    def postgres_cluster_identifier(self, value):
        self._postgres_cluster_identifier = value

    @property
    def do_not_send_ses_suppressed_bounce_notifications(self):
        return self._do_not_send_ses_suppressed_bounce_notifications

    @do_not_send_ses_suppressed_bounce_notifications.setter
    def do_not_send_ses_suppressed_bounce_notifications(self, value):
        self._do_not_send_ses_suppressed_bounce_notifications = value

    @property
    def ses_alert_slack_channel(self):
        return self._ses_alert_slack_channel

    @ses_alert_slack_channel.setter
    def ses_alert_slack_channel(self, value):
        self._ses_alert_slack_channel = value

    @property
    def bearer_token(self):
        if self._bearer_token is None:
            raise self.UndefinedValueError("bearer_token")
        return self._bearer_token

    @bearer_token.setter
    def bearer_token(self, value):
        self._bearer_token = value

    @property
    def self_monitoring_slack_channel(self):
        if self._self_monitoring_slack_channel is None:
            raise self.UndefinedValueError("self_monitoring_slack_channel")
        return self._self_monitoring_slack_channel

    @self_monitoring_slack_channel.setter
    def self_monitoring_slack_channel(self, value):
        self._self_monitoring_slack_channel = value

    @property
    def routing_tags_to_slack_channels_mapping(self):
        if self._routing_tags_to_slack_channels_mapping is None:
            raise self.UndefinedValueError("routing_tags_to_slack_channels_mapping")
        return self._routing_tags_to_slack_channels_mapping

    @routing_tags_to_slack_channels_mapping.setter
    def routing_tags_to_slack_channels_mapping(self, value):
        self._routing_tags_to_slack_channels_mapping = value

    @property
    def lambda_name(self):
        if self._lambda_name is None:
            if self._slug is None:
                raise self.UndefinedValueError("lambda_name")
            self._lambda_name = self.slug
        return self._lambda_name

    @lambda_name.setter
    def lambda_name(self, value):
        self._lambda_name = value

    @property
    def lambda_role_name(self):
        self.check_defined()
        return self._lambda_role_name

    @lambda_role_name.setter
    def lambda_role_name(self, value):
        self._lambda_role_name = value

    @property
    def event_bridge_rule_name(self):
        if self._event_bridge_rule_name is None:
            self._event_bridge_rule_name = f"rule-{self.slug}"
        return self._event_bridge_rule_name

    @event_bridge_rule_name.setter
    def event_bridge_rule_name(self, value):
        self._event_bridge_rule_name = value

    @property
    def dynamodb_table_name(self):
        if self._dynamodb_table_name is None:
            self._dynamodb_table_name = f"tbl-{self.slug}"
        return self._dynamodb_table_name

    @dynamodb_table_name.setter
    def dynamodb_table_name(self, value):
        self._dynamodb_table_name = value

    @property
    def alert_system_lambda_log_group_name(self):
        return f"/aws/lambda/{self.lambda_name}"

    @property
    def lambda_timeout(self):
        return 300

    @property
    def slug(self):
        if self._slug is None:
            self._slug = self.lambda_name
        return self._slug

    @slug.setter
    def slug(self, value):
        self._slug = value
