"""
AWS ECS config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


class EKSAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._health_check_path = None

    @property
    def health_check_path(self):
        self.check_defined()
        return self._health_check_path

    @health_check_path.setter
    def health_check_path(self, value):
        self._health_check_path = value
