"""
Standard ECS maintainer.

"""

from horey.h_logger import get_logger

logger = get_logger()


class AWSLambdaAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api
        self.ecs_api = None
        self.cloudwatch_api = None

    def set_apis(self, ecs_api=None, cloudwatch_api=None):
        """
        Set api to manage ecs tasks.

        :param cloudwatch_api:
        :param ecs_api:
        :return:
        """

        self.ecs_api = ecs_api
        self.cloudwatch_api = cloudwatch_api

    def provision(self):
        """
        Provision ECS infrastructure.

        :return:
        """

        self.cloudwatch_api.provision()
        breakpoint()
        self.provision_logging()

        if self.configuration.ecr_repository_name:
            self.provision_repository()

        self.provision_lambda_role()
        self.provision_events_rule()

        # todo: self.provision_alert_system([])

    def update(self):
        """

        :return:
        """

        breakpoint()
