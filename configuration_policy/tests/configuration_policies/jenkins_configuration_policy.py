import sys
import os
from enum import Enum
import pdb

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))


from grade_configuration_policy import GradeConfigurationPolicy


class JenkinsConfigurationPolicy(GradeConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._jenkins_host = None
        self._jenkins_username = None
        self._jenkins_token = None
        self._jenkins_protocol = None
        self._jenkins_port = None
        self._jenkins_timeout = None
        self._deployment_method = None

    @property
    def jenkins_host(self):
        if self.int_grade > self.GradeValue.LOCAL.value:
            return f"jenkins-{self.grade.lower()}"

        if self._jenkins_host is None:
            raise ValueError("jenkins_host was not set")

        return self._jenkins_host

    @jenkins_host.setter
    def jenkins_host(self, value):
        if self.int_grade > self.GradeValue.LOCAL.value:
            raise ValueError(f"Setting hostname to {value} in environment grade {self.grade}")
        self._jenkins_host = value

    @property
    def jenkins_username(self):
        return self._jenkins_username

    @jenkins_username.setter
    def jenkins_username(self, value):
        self._jenkins_username = value

    @property
    def jenkins_token(self):
        return self._jenkins_token

    @jenkins_token.setter
    def jenkins_token(self, value):
        self._jenkins_token = value

    @property
    def jenkins_protocol(self):
        return self._jenkins_protocol

    @jenkins_protocol.setter
    def jenkins_protocol(self, value):
        self._jenkins_protocol = value

    @property
    def jenkins_port(self):
        return self._jenkins_port

    @jenkins_port.setter
    def jenkins_port(self, value):
        self._jenkins_port = value

    @property
    def jenkins_timeout(self):
        return self._jenkins_timeout

    @jenkins_timeout.setter
    def jenkins_timeout(self, value):
        self._jenkins_timeout = value

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
