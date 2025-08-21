"""
EC2 API config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


class EC2APIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._name = None
        self._ip_permissions = None

    @property
    def ip_permissions(self):
        if self._ip_permissions is None:
            raise self.UndefinedValueError("ip_permissions")
        return self._ip_permissions

    @ip_permissions.setter
    def ip_permissions(self, value):
        self._ip_permissions = value

    @property
    def name(self):
        if self._name is None:
            raise self.UndefinedValueError("name")
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

