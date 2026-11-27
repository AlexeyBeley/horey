from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class DockerAPIConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._host = None

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value
