"""
Standard Cloudwatch maintainer.

"""

from horey.h_logger import get_logger
from horey.aws_api.aws_services_entities.cloud_watch_log_group import CloudWatchLogGroup
logger = get_logger()


class CloudwatchAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api

    def provision(self):
        """
        Provision ECS infrastructure.

        :return:
        """

        self.provision_log_group()

    def provision_log_group(self):
        """
        Provision log group.

        :return:
        """

        log_group = CloudWatchLogGroup({})
        log_group.region = self.environment_api.region
        log_group.name = self.configuration.log_group_name
        log_group.retention_in_days = self.configuration.retention_in_days
        log_group.tags = {tag["Key"]: tag["Value"] for tag in self.environment_api.configuration.tags}
        log_group.tags["name"] = log_group.name
        self.environment_api.aws_api.cloud_watch_logs_client.provision_log_group(log_group)
        return log_group

    def update(self):
        """

        :return:
        """

        breakpoint()
