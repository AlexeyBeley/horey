"""
AWS Lambda config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


class AWSLambdaAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._container_ports = None

    @property
    def container_ports(self):
        if self._container_ports is None:
            raise self.UndefinedValueError("container_ports")
        return self._container_ports

    @container_ports.setter
    def container_ports(self, value):
        self._container_ports = value
