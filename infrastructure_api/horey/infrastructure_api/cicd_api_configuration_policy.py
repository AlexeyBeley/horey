"""
AWS Lambda config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


class CICDAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._build_environment_variable = None

    @property
    def build_environment_variable(self):
        if self._build_environment_variable is None:
            raise self.UndefinedValueError("build_environment_variable")
        return self._build_environment_variable  

    @build_environment_variable.setter
    def build_environment_variable(self, value):
        self._build_environment_variable = value
