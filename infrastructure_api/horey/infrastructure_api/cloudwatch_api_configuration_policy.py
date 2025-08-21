"""
AWS Lambda config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


class CloudwatchAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._log_group_name = None
        self._retention_in_days = None

    @property
    def retention_in_days(self):
        if self._retention_in_days is None:
            self._retention_in_days = 30
        return self._retention_in_days

    @retention_in_days.setter
    def retention_in_days(self, value):
        self._retention_in_days = value

    @property
    def log_group_name(self):
        if self._log_group_name is None:
            raise self.UndefinedValueError("log_group_name")
        return self._log_group_name

    @log_group_name.setter
    def log_group_name(self, value):
        self._log_group_name = value

