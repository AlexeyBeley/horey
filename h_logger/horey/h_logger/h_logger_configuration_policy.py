import os
from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class HLoggerConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._error_level_file_path = None

    @property
    def error_level_file_path(self):
        return self._error_level_file_path

    @error_level_file_path.setter
    def error_level_file_path(self, value):
        self._error_level_file_path = value