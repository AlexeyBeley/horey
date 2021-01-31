from configuration_policy import Configuration
import pdb
from enum import Enum


class JenkinsDeployConfiguration(InfrastructureConfiguration):
    def __init__(self):
        super().__init__()
        self._deployment_method = None

    @property
    def deployment_method(self):
        return self._deployment_method

    @deployment_method.setter
    def deployment_method(self, value):
        if value not in self.DeploymentMethod:
            raise ValueError(value)

        self._deployment_method = value

    class DeploymentMethod(Enum):
        LOCAL_NATIVE = 0
        LOCAL_DOCKER = 1
        ECS = 3
