import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "horey", "configuration_policy"))


from configuration_policy import ConfigurationPolicy


class EnvironmentConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._name = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value


