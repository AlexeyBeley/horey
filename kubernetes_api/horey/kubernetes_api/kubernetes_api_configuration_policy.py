import os
from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class KubernetesAPIConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self.token = None
        self.cadata = None
        self.endpoint = None
        self._kubernetes_api_cache_dir = None

    @property
    def kubernetes_api_cache_dir(self):
        if self._kubernetes_api_cache_dir is None:
            raise ValueError("kubernetes_api_cache_dir was not set")
        return self._kubernetes_api_cache_dir

    @kubernetes_api_cache_dir.setter
    def kubernetes_api_cache_dir(self, value):
        self._kubernetes_api_cache_dir = value
        os.makedirs(self._kubernetes_api_cache_dir, exist_ok=True)
