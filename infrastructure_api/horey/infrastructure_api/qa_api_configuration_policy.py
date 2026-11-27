"""
QA config

"""

from pathlib import Path 
from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


class QAAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._secrets_region = None
        self._tests_data_directory_path = None

    @property
    def secrets_region(self):
        if self._secrets_region is None:
            raise self.UndefinedValueError("secrets_region")
        return self._secrets_region

    @secrets_region.setter
    def secrets_region(self, value):
        self._secrets_region = value

    
    @property
    def tests_data_directory_path(self):
        if self._tests_data_directory_path is None:
            self._tests_data_directory_path = Path("/tmp/horey_tests_data")
            self._tests_data_directory_path.mkdir(exist_ok=True)
        return self._tests_data_directory_path 
