from pathlib import Path
from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class CWrapperConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._password = None

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value
