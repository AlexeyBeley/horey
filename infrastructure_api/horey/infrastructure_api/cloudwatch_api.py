"""
Standard Cloudwatch maintainer.

"""

from horey.h_logger import get_logger
from horey.aws_api.aws_services_entities.cloud_watch_log_group import CloudWatchLogGroup
from horey.aws_api.aws_services_entities.cloud_watch_alarm import CloudWatchAlarm
from horey.infrastructure_api.cloudwatch_api_configuration_policy import CloudwatchAPIConfigurationPolicy
logger = get_logger()


class CloudwatchAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration: CloudwatchAPIConfigurationPolicy, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api

    def provision_log_group(self, log_group_name):
        """
        Provision log group.

        :return:
        """

        log_group = CloudWatchLogGroup({})
        log_group.region = self.environment_api.region
        log_group.name = log_group_name
        log_group.retention_in_days = self.configuration.retention_in_days
        log_group.tags = {tag["Key"]: tag["Value"] for tag in self.environment_api.configuration.tags}
        log_group.tags["name"] = log_group.name
        self.environment_api.aws_api.cloud_watch_logs_client.provision_log_group(log_group)
        return log_group

    def get_cloudwatch_log_group(self, log_group_name=None):
        """
        Provision log group

        @return:
        """

        log_group = CloudWatchLogGroup({})
        log_group.region = self.environment_api.region
        log_group.name = log_group_name

        if self.environment_api.aws_api.cloud_watch_logs_client.update_log_group_information(log_group):
            return log_group

        self.environment_api.aws_api.cloud_watch_logs_client.clear_cache(CloudWatchLogGroup)

        if self.environment_api.aws_api.cloud_watch_logs_client.update_log_group_information(log_group):
            return log_group

        raise RuntimeError(f"Could not update log group information '{log_group_name}' in region '{self.environment_api.configuration.region}'")

    def put_cloudwatch_log_lines(self, log_group_name, lines):
        """
        Make sure the group exist and put the log lines in it.

        :param log_group_name:
        :param lines:
        :return:
        """

        log_group = self.get_cloudwatch_log_group(log_group_name)

        return self.environment_api.aws_api.cloud_watch_logs_client.put_log_lines(log_group, lines)

    # pylint: disable = unused-argument, too-many-arguments, too-many-positional-arguments, too-many-locals
    def provision_alarm(self, name=None,
                                   insufficient_data_actions=None,
                                   metric_name=None,
                                   namespace=None,
                                   statistic=None,
                                   dimensions=None,
                                   period=None,
                                   evaluation_periods=None,
                                   datapoints_to_alarm=None,
                                   threshold=None,
                                   comparison_operator=None,
                                   treat_missing_data=None,
                                   alarm_description=None,
                                   alarm_actions=None,
                                   ok_actions=None):
        """
        Provision cloudwatch metric Lambda errors.
        Lambda service metric shows the count of failed Lambda executions.

        :return:
        """

        kwargs = locals()
        del kwargs["self"]

        alarm = CloudWatchAlarm(kwargs,from_cache=True)
        base_alarm = CloudWatchAlarm({})
        for key in alarm.__dict__:
            if key not in base_alarm.__dict__:
                raise ValueError(f"Unknown key '{key}' in kwargs '{kwargs}'")
        alarm.region = self.environment_api.region
        self.environment_api.aws_api.cloud_watch_client.set_cloudwatch_alarm(alarm)

        return alarm
