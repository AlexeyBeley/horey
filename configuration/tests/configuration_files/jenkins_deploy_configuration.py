from jenkins_ops_configuration import JenkinsOpsConfiguration
from infrastructure_configuration import InfrastructureConfiguration
import pdb
from enum import Enum


class JenkinsDeployConfiguration(InfrastructureConfiguration, JenkinsOpsConfiguration):
    def __init__(self):
        super().__init__()
        self._deployment_method = None

    @property
    def deployment_method(self):
        return

    @deployment_method.setter
    def deployment_method(self, value):
        pdb.set_trace()
        if value not in self.DeploymentMethod:
            raise ValueError(value)

        self._deployment_method = value

    class DeploymentMethod(Enum):
        LOCAL_NATIVE = 0
        LOCAL_DOCKER = 1
