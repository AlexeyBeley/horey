import os
from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class KubernetesAPIConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self.token = None
        self.cadata = None
        self.endpoint = None
        self._kubernetes_api_cache_dir = None
        self._cluster_name = None

    @property
    def kubernetes_api_cache_dir(self):
        if self._kubernetes_api_cache_dir is None:
            raise ValueError("kubernetes_api_cache_dir was not set")
        return self._kubernetes_api_cache_dir

    @kubernetes_api_cache_dir.setter
    def kubernetes_api_cache_dir(self, value):
        self._kubernetes_api_cache_dir = value
        os.makedirs(self._kubernetes_api_cache_dir, exist_ok=True)

    @property
    def cluster_name(self):
        if self._cluster_name is None:
            raise ValueError("cluster_name was not set")
        return self._cluster_name

    @cluster_name.setter
    def cluster_name(self, value):
        self._cluster_name = value

    @property
    def namespace_cache_dir_path(self):
        ret = os.path.join(self.kubernetes_api_cache_dir, self.cluster_name)
        os.makedirs(ret, exist_ok=True)
        return ret
