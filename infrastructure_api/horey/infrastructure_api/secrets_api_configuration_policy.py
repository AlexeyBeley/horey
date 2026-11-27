"""
AWS Lambda config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


class SecretsAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._region = None

    @property
    def region(self):
        self.check_defined()
        return self._region

    @region.setter
    def region(self, value):
        assert isinstance(value, str)
        self._region = value
