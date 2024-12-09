"""
AWS ECS config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


class ECSAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._load_balancer_target_group_arn = None
        self._container_ports = None

    @property
    def container_ports(self):
        if self._container_ports is None:
            raise self.UndefinedValueError("container_ports")
        return self._container_ports

    @container_ports.setter
    def container_ports(self, value):
        self._container_ports = value

    @property
    def load_balancer_target_group_arn(self):
        if self._load_balancer_target_group_arn is None:
            raise self.UndefinedValueError("load_balancer_target_group_arn")
        return self._load_balancer_target_group_arn

    @load_balancer_target_group_arn.setter
    def load_balancer_target_group_arn(self, value):
        self._load_balancer_target_group_arn = value
