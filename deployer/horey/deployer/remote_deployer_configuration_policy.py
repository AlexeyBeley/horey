from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class RemoteDeployerConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._cleanup = None

    @property
    def cleanup(self):
        if self._cleanup is None :
            raise ValueError("Cleanup not set")
        return self._cleanup

    @cleanup.setter
    def cleanup(self, value):
        if not isinstance(value, bool):
            raise ValueError(f"cleanup must be bool, received: '{type(value)}'")
        self._cleanup = value
