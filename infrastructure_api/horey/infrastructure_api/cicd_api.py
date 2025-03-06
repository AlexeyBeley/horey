"""
Standard Load balancing maintainer.

"""
from horey.infrastructure_api.cloudwatch_api_configuration_policy import CloudwatchAPIConfigurationPolicy
from horey.infrastructure_api.cloudwatch_api import CloudwatchAPI

from horey.h_logger import get_logger

logger = get_logger()


class CICDAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api
        self._cloudwatch_api = None
        self.ecs_api = None

    @property
    def cloudwatch_api(self):
        """
        Standard.

        :return:
        """
        if self._cloudwatch_api is None:
            config = CloudwatchAPIConfigurationPolicy()
            self._cloudwatch_api = CloudwatchAPI(configuration=config, environment_api=self.environment_api)
        return self._cloudwatch_api

    def set_api(self, ecs_api=None, cloudwatch_api=None):
        """
        Set apis.

        :param cloudwatch_api:
        :param ecs_api:
        :return:
        """

        self.ecs_api = ecs_api
        try:
            ecs_api.configuration.adhoc_task_name
        except ecs_api.configuration.UndefinedValueError:
            ecs_api.configuration.adhoc_task_name = "hagent"

        if cloudwatch_api:
            self._cloudwatch_api = cloudwatch_api

        try:
            self.cloudwatch_api.configuration.log_group_name
        except self._cloudwatch_api.configuration.UndefinedValueError:
            self.cloudwatch_api.configuration.log_group_name = ecs_api.configuration.cloudwatch_log_group_name

        self.ecs_api.set_api(cloudwatch_api=self.cloudwatch_api)

    def provision(self):
        """
        Provision CICD infrastructure.

        :return:
        """

        ecs_task_definition = self.ecs_api.provision_ecs_task_definition(self.ecs_api.ecr_repo_uri + ":latest")
        self.cloudwatch_api.provision()

    def update(self):
        """

        :return:
        """

        overrides = {"containerOverrides": [{"name": "mgmt-tools-development-hagent",
                                             "environment": [{"name": key, "value": value} for key, value in
                                                             self.configuration.build_environment_variable.items()]}]}
        breakpoint()
        ret = self.ecs_api.start_task(overrides=overrides)
