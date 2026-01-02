"""
Standard.

"""

from horey.h_logger import get_logger
from horey.infrastructure_api.scheduler_api_configuration_policy import SchedulerAPIConfigurationPolicy

logger = get_logger()


class SchedulerAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration:SchedulerAPIConfigurationPolicy, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api

