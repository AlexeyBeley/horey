from horey.configuration_policy.configuration_policy import ConfigurationPolicy


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


