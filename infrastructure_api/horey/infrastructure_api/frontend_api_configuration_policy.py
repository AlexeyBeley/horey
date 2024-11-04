"""
AWS EnvironmentAPI config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


class FrontendAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._bucket_name = None

    @property
    def bucket_name(self):
        if self._bucket_name is None:
            raise self.UndefinedValueError("bucket_name")
        return self._bucket_name

    @bucket_name.setter
    def bucket_name(self, value):
        self._bucket_name = value