"""
Alerts maintainer.

"""
import datetime
import json
import os.path
import sys

from horey.alert_system.alert_system import AlertSystem
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy
from horey.alert_system.lambda_package.notification_channels.notification_channel_slack import NotificationChannelSlack, \
    NotificationChannelSlackConfigurationPolicy
from horey.alert_system.lambda_package.notification import Notification
from horey.alert_system.lambda_package.message_ses_default import MessageSESDefault
from horey.alert_system.postgres.postgres_cluster_monitoring_configuration_policy import \
    PostgresClusterMonitoringConfigurationPolicy
from horey.alert_system.postgres.postgres_cluster_writer_monitoring_configuration_policy import \
    PostgresClusterWriterMonitoringConfigurationPolicy
from horey.alert_system.postgres.postgres_alert_manager_configuration_policy import \
    PostgresAlertManagerConfigurationPolicy
from horey.alert_system.postgres.postgres_alert_builder import \
    PostgresAlertBuilder


class AlertsAPI:
    """
    Manage Frontend.

    """

    def __init__(self, configuration, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api

        has2_config = AlertSystemConfigurationPolicy()
        has2_config.horey_repo_path = self.configuration.horey_repo_path
        has2_config.do_not_send_ses_suppressed_bounce_notifications = self.configuration.do_not_send_ses_suppressed_bounce_notifications
        has2_config.sns_topic_name = self.configuration.sns_topic_name

        has2_config.region = self.environment_api.configuration.region
        self.alert_system = AlertSystem(has2_config)
        self.generate_notification_channels_configuration()

    def generate_notification_channels_configuration(self):
        """
        Generate slack api files.

        :return:
        """

        configuration = NotificationChannelSlackConfigurationPolicy()
        dict_mappings = self.configuration.route_tags_to_slack_channels_mapping
        dict_mappings.update(
            {Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG: self.configuration.self_monitoring_slack_channel})
        if self.configuration.ses_alert_slack_channel:
            dict_mappings.update(
                {
                    MessageSESDefault.ROUTING_TAG: self.configuration.ses_alert_slack_channel})

        configuration.tag_to_channel_mapping = dict_mappings
        configuration.bearer_token = self.configuration.bearer_token

        self.alert_system.configuration.notification_channels = [
            sys.modules[NotificationChannelSlack.__module__].__file__]
        self.alert_system.configuration.lambda_name = self.configuration.lambda_name
        self.alert_system.configuration.dynamodb_table_name = self.configuration.dynamodb_table_name
        self.alert_system.configuration.region = self.environment_api.configuration.region
        self.alert_system.configuration.tags = self.environment_api.configuration.tags

        slack_channel_configuration_file_path = os.path.join(self.alert_system.configuration.deployment_directory_path,
                                                             NotificationChannelSlack.CONFIGURATION_FILE_NAME)
        configuration.generate_configuration_file(slack_channel_configuration_file_path)

        alert_system_configuration_file_path = os.path.join(self.alert_system.configuration.deployment_directory_path,
                                                            AlertSystemConfigurationPolicy.ALERT_SYSTEM_CONFIGURATION_FILE_PATH)
        self.alert_system.configuration.generate_configuration_file(alert_system_configuration_file_path)

        self.configuration.files = [slack_channel_configuration_file_path, alert_system_configuration_file_path]

    def provision(self):
        """
        Provision frontend.

        :return:
        """

        self.environment_api.clear_cache()
        self.provision_sns_topic()
        self.provision_dynamodb()
        self.provision_event_bridge_rule()
        self.provision_lambda_role()
        aws_lambda = self.provision_lambda()
        self.provision_event_bridge_rule(aws_lambda=aws_lambda)
        self.provision_sns_subscription()
        self.provision_log_group()
        self.provision_self_monitoring()
        return True

    def generate_postgres_cluster_alarms(self, cluster_id):
        """
        Generate alerts per resource: RDS Postgres Cluster

        :param cluster_id:
        :return:
        """

        cluster = self.environment_api.get_rds_cluster(cluster_id)
        alerts_builder = PostgresAlertBuilder(cluster=cluster)
        return self.alert_system.generate_resource_alarms(alerts_builder)

    def update(self, resource_alarms=None):
        """

        :return:
        """

        self.provision_lambda()

        if resource_alarms:
            self.provision_resource_alarms(resource_alarms)
        return True

    def provision_resource_alarms(self, resource_alarms):
        """
        Provision generated alarms.

        :param resource_alarms:
        :return:
        """

        for alarm in resource_alarms:
            self.environment_api.provision_cloudwatch_alarm_object(alarm)
        return True

    def provision_sns_topic(self):
        """
        Alert system sns topic

        :return:
        """
        self.environment_api.provision_sns_topic(sns_topic_name=self.configuration.sns_topic_name)

    def provision_dynamodb(self):
        """
        Used for alert status storing.
        {'sensor_uid': {'S': 'test_manual'}, 'alarm_state': {'M': {'cooldown_time': {'N': '300'}, 'epoch_triggered': {'N': '11111111111111'}}}}
        {'sensor_uid': {'S': 'test_manual2'}}

        :return:
        """

        attribute_definitions = [
            {
                "AttributeName": "alarm_name",
                "AttributeType": "S"
            }
        ]

        key_schema = [
            {
                "AttributeName": "alarm_name",
                "KeyType": "HASH"
            }
        ]

        self.environment_api.provision_dynamodb(dynamodb_table_name=self.configuration.dynamodb_table_name,
                                                attribute_definitions=attribute_definitions,
                                                key_schema=key_schema)

    def provision_lambda(self):
        """
        Provision Alert System Lambda

        :return:
        """

        topic = self.environment_api.get_sns_topic(self.configuration.sns_topic_name)
        events_rule = self.environment_api.get_event_bridge_rule(self.configuration.event_bridge_rule_name)

        zip_file_path = self.alert_system.build_and_validate(self.configuration.files)
        policy = {
            "Version": "2012-10-17",
            "Id": "default",
            "Statement": [
                {
                    "Sid": f"trigger_from_topic_{topic.name}",
                    "Effect": "Allow",
                    "Principal": {"Service": "sns.amazonaws.com"},
                    "Action": "lambda:InvokeFunction",
                    "Resource": None,
                    "Condition": {"ArnLike": {"AWS:SourceArn": topic.arn}},
                },
                {"Sid": f"trigger_{self.configuration.lambda_name}",
                 "Effect": "Allow",
                 "Principal": {"Service": "events.amazonaws.com"},
                 "Action": "lambda:InvokeFunction",
                 "Resource": None,
                 "Condition": {"ArnLike": {
                     "AWS:SourceArn": events_rule.arn}}},
                {
                    "Sid": "AlarmAction",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.alarms.cloudwatch.amazonaws.com"
                    },
                    "Action": "lambda:InvokeFunction",
                    "Resource": None,
                    "Condition": {
                        "StringEquals": {
                            "AWS:SourceAccount": self.environment_api.aws_api.cloud_watch_client.account_id
                        }
                    }
                }
            ]
        }

        return self.environment_api.deploy_lambda(lambda_name=self.configuration.lambda_name,
                                                  handler="lambda_handler.lambda_handler",
                                                  timeout=self.configuration.lambda_timeout,
                                                  memory_size=512,
                                                  policy=policy,
                                                  role_name=self.configuration.lambda_role_name,
                                                  zip_file_path=zip_file_path
                                                  )

    def provision_event_bridge_rule(self, aws_lambda=None):
        """
        Provision event bridge rule to trigger the lambda.

        :return:
        """

        description = "Triggering rule for alert system lambda"
        self.environment_api.provision_event_bridge_rule(aws_lambda=aws_lambda,
                                                         event_bridge_rule_name=self.configuration.event_bridge_rule_name,
                                                         description=description)

    def provision_lambda_role(self):
        """
        Provision the alert_system receiving Lambda role.

        :return:
        """

        assume_role_policy_document = json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        })

        inline_policies = [self.generate_inline_dynamodb_policy(), self.generate_inline_cloudwatch_policy()]
        return self.environment_api.provision_iam_role(name=self.configuration.lambda_role_name,
                                                       description="HAS2 lambda",
                                                       assume_role_policy_document=assume_role_policy_document,
                                                       managed_policies_arns=[
                                                           "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"],
                                                       inline_policies=inline_policies)

    def provision_sns_subscription(self):
        """
        Provision the lambda subscription in the SNS topic
        :return:
        """

        self.environment_api.provision_sns_subscription(sns_topic_name=self.configuration.sns_topic_name,
                                                        subscription_name=self.configuration.sns_subscription_name,
                                                        lambda_name=self.configuration.lambda_name)

    def provision_log_group(self):
        """
        Provision Lambda log group.
        On a fresh provisioning self monitoring will have no log group to monitor.
        Until first lambda invocation.

        :return:
        """

        self.environment_api.provision_log_group(log_group_name=self.configuration.alert_system_lambda_log_group_name)

    def generate_inline_dynamodb_policy(self):
        """
        DynamoDB access

        :return:
        """
        dynamodb = self.environment_api.get_dynamodb(self.configuration.dynamodb_table_name)
        statements = [
            {
                "Action": [
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:GetItem",
                    "dynamodb:Scan",
                    "dynamodb:DescribeTable",
                    "dynamodb:ListTagsOfResource",
                    "dynamodb:DeleteItem"
                ],
                "Resource": [
                    dynamodb.arn,
                    f"{dynamodb.arn}//index/*"
                ],
                "Effect": "Allow"
            }
        ]
        return self.environment_api.generate_inline_policy(name="inline_dynamodb",
                                                           description="DynamoDB access policy",
                                                           statements=statements)

    def generate_inline_cloudwatch_policy(self):
        """
        Cloudwatch access

        :return:
        """
        statements = [
            {
                "Action": [
                    "cloudwatch:SetAlarmState"
                ],
                "Resource": [
                    f"arn:aws:cloudwatch:{self.environment_api.configuration.region}:{self.environment_api.aws_api.dynamodb_client.account_id}:alarm:*"
                ],
                "Effect": "Allow"
            }
        ]

        return self.environment_api.generate_inline_policy(name="inline_cloudwatch",
                                                           description="Cloudwatch access policy",
                                                           statements=statements)

    # pylint: disable = too-many-arguments
    def provision_cloudwatch_logs_alarm(self, log_group_name, filter_text, metric_uid, routing_tags, dimensions=None,
                                        alarm_description=None
                                        ):
        """
        Provision Cloud watch logs based alarm.

        @return:
        :param routing_tags:
        :param metric_uid:
        :param filter_text:
        :param message_dict: extensive data to be stored in alert description
        :param log_group_name:
        """

        if not alarm_description:
            alarm_description = {}
        alarm_description["log_group_name"] = log_group_name
        alarm_description["log_group_filter_pattern"] = filter_text
        alarm_description["routing_tags"] = routing_tags
        if not log_group_name or not isinstance(log_group_name, str):
            raise ValueError(f"{log_group_name=}")
        if not isinstance(routing_tags, list):
            raise ValueError(
                f"Routing tags must be a list, received: '{alarm_description}'"
            )
        if len(routing_tags) == 0:
            raise ValueError(f"No routing tags: received: '{alarm_description}'")

        metric_filter = self.environment_api.provision_log_group_metric_filter(
            name=f"has2-metric-filter-lambda-{self.configuration.lambda_name}-{metric_uid}",
            log_group_name=log_group_name, filter_text=filter_text)
        if len(metric_filter.metric_transformations) != 1:
            raise NotImplementedError(
                f"Unhandled situation when more then one metric transformation {metric_filter.metric_transformations}")

        alarm = self.provision_cloudwatch_alarm(name=f"has2-alarm-{log_group_name}-{metric_uid}",
                                                alarm_description=json.dumps(alarm_description),
                                                metric_name=metric_filter.metric_transformations[0]["metricName"],
                                                namespace=log_group_name,
                                                dimensions=dimensions,
                                                statistic="Sum",
                                                period=300,
                                                evaluation_periods=1,
                                                datapoints_to_alarm=1,
                                                threshold=0.0,
                                                comparison_operator="GreaterThanThreshold",
                                                treat_missing_data="notBreaching"
                                                )

        return alarm

    # pylint: disable = too-many-arguments
    def provision_cloudwatch_alarm(self, name=None,
                                   alarm_description=None,
                                   metric_name=None,
                                   namespace=None,
                                   dimensions=None,
                                   statistic=None,
                                   period=None,
                                   evaluation_periods=None,
                                   datapoints_to_alarm=None,
                                   threshold=None,
                                   comparison_operator=None,
                                   treat_missing_data=None):
        """
        Provision cloudwatch alarm - add self topic to it.

        :param name:
        :param alarm_description:
        :param metric_name:
        :param namespace:
        :param statistic:
        :param period:
        :param evaluation_periods:
        :param datapoints_to_alarm:
        :param threshold:
        :param comparison_operator:
        :param treat_missing_data:
        :return:
        """

        topic = self.environment_api.get_sns_topic(self.configuration.sns_topic_name)

        return self.environment_api.provision_cloudwatch_alarm(name=name,
                                                               alarm_description=alarm_description,
                                                               metric_name=metric_name,
                                                               namespace=namespace,
                                                               dimensions=dimensions,
                                                               statistic=statistic,
                                                               period=period,
                                                               evaluation_periods=evaluation_periods,
                                                               datapoints_to_alarm=datapoints_to_alarm,
                                                               threshold=threshold,
                                                               comparison_operator=comparison_operator,
                                                               treat_missing_data=treat_missing_data,
                                                               ok_actions=[topic.arn],
                                                               alarm_actions=[topic.arn],
                                                               insufficient_data_actions=[]
                                                               )

    def provision_self_monitoring(self):
        """
        Provision self monitoring different parts.

        @return:
        """

        self.provision_self_monitoring_log_error_alarm()
        self.trigger_self_monitoring_log_error_alarm()

        self.provision_self_monitoring_log_timeout_alarm()
        self.trigger_self_monitoring_log_timeout_alarm()

        alarm = self.provision_self_monitoring_errors_metric_alarm()
        self.environment_api.trigger_cloudwatch_alarm(alarm, "Explicitly changed state to ALARM")

        alarm = self.provision_self_monitoring_duration_alarm()
        self.environment_api.trigger_cloudwatch_alarm(alarm, "Explicitly changed state to ALARM")

        alarm = self.provision_self_monitoring_event_bridge_successful_invocations_alarm()
        self.environment_api.aws_api.cloud_watch_client.set_alarm_state(alarm, "ALARM")
        return True

    def provision_self_monitoring_log_error_alarm(self):
        """
        Find [ERROR] log messages in self log.

        @return:
        """

        filter_text = f'"{AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_LOG_ERROR_FILTER_PATTERN}"'
        alarm_description = {
            "lambda_name": self.configuration.lambda_name,
            AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY: AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY}

        return self.provision_cloudwatch_logs_alarm(self.configuration.alert_system_lambda_log_group_name,
                                                    filter_text,
                                                    "error",
                                                    [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG],
                                                    alarm_description=alarm_description,
                                                    )

    def provision_self_monitoring_log_timeout_alarm(self):
        """
        Find lambda timeout messages in self log.

        @return:
        """

        filter_text = AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_LOG_TIMEOUT_FILTER_PATTERN
        alarm_description = {"lambda_name": self.configuration.lambda_name,
                             AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY: AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY}

        return self.provision_cloudwatch_logs_alarm(self.configuration.alert_system_lambda_log_group_name,
                                                    filter_text,
                                                    "timeout",
                                                    [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG],
                                                    alarm_description=alarm_description
                                                    )

    def provision_self_monitoring_errors_metric_alarm(self):
        """
        Provision cloudwatch metric Lambda errors.
        Lambda service metric shows the count of failed Lambda executions.

        @return:
        """

        alarm_description = {"routing_tags": [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG],
                             "lambda_name": self.configuration.lambda_name,
                             AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY: AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY}
        alarm = self.provision_cloudwatch_alarm(
            name=f"has2-alarm-{self.configuration.lambda_name}-metric-errors",
            alarm_description=json.dumps(alarm_description),
            metric_name="Errors",
            namespace="AWS/Lambda",
            statistic="Average",
            period=300,
            evaluation_periods=1,
            datapoints_to_alarm=1,
            threshold=1.0,
            comparison_operator="GreaterThanThreshold",
            treat_missing_data="notBreaching",
            dimensions=[
                {"Name": "FunctionName", "Value": self.configuration.lambda_name}
            ]
        )

        return alarm

    def provision_self_monitoring_duration_alarm(self):
        """
        Check self metric for running to long.

        @return:
        """

        alarm_description = {"routing_tags": [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG],
                             "lambda_name": self.configuration.lambda_name,
                             AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY: AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY}

        alarm = self.provision_cloudwatch_alarm(
            name=f"has2-alarm-{self.configuration.lambda_name}-metric-duration",
            alarm_description=json.dumps(alarm_description),
            metric_name="Duration",
            namespace="AWS/Lambda",
            statistic="Average",
            period=300,
            evaluation_periods=1,
            datapoints_to_alarm=1,
            threshold=self.configuration.lambda_timeout * 0.6 * 1000,
            comparison_operator="GreaterThanThreshold",
            treat_missing_data="notBreaching",
            dimensions=[
                {"Name": "FunctionName", "Value": self.configuration.lambda_name}
            ]
        )

        return alarm

    def provision_self_monitoring_event_bridge_successful_invocations_alarm(self):
        """
        Provision cloudwatch metric EventBridge Successful Invocations
        It should be equal to 5 in 5 minutes.

        @return:
        """

        alarm_description = {"routing_tags": [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG],
                             "lambda_name": self.configuration.lambda_name,
                             AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY: AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_TYPE_KEY}

        alarm = self.provision_cloudwatch_alarm(
            name=f"has2-alarm-{self.configuration.lambda_name}-eventbridge-successful-invocations",
            alarm_description=json.dumps(alarm_description),
            metric_name="Invocations",
            namespace="AWS/Events",
            statistic="Sum",
            period=300,
            evaluation_periods=1,
            datapoints_to_alarm=1,
            threshold=4.0,
            comparison_operator="LessThanThreshold",
            treat_missing_data="notBreaching",
            dimensions=[
                {"Name": "RuleName", "Value": self.configuration.event_bridge_rule_name}
            ]
        )

        return alarm

    def trigger_self_monitoring_log_error_alarm(self):
        """
        Trigger the alarm using cloudwatch log stream filter metric.

        :return:
        """
        return self.environment_api.put_cloudwatch_log_lines(self.configuration.alert_system_lambda_log_group_name, [
            f"{AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_LOG_ERROR_FILTER_PATTERN}: Neo, the Horey has you!"])

    def trigger_self_monitoring_log_timeout_alarm(self):
        """
        Test timeout alarm

        :return:
        """

        return self.environment_api.put_cloudwatch_log_lines(self.configuration.alert_system_lambda_log_group_name, [
            f"{AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_LOG_TIMEOUT_FILTER_PATTERN}: Neo, the Horey has you!"])

    def build_and_validate(self, event):
        """
        Build and run on event.

        :param event:
        :return:
        """

        zip_file_path = self.alert_system.build_and_validate(self.configuration.files, event)
        breakpoint()

    def get_all_metrics(self, namespace):
        breakpoint()
        ret = list(self.environment_api.aws_api.cloud_watch_client.yield_client_metrics(self.environment_api.region,
                                                                                        {"Namespace": namespace}))
