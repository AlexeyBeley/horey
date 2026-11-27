import os
from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class GCPAPIConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._gcp_api_regions = None
        self._accounts_file = None
        self._gcp_account = None
        self._gcp_api_cache_dir = None

    @property
    def gcp_api_regions(self):
        if self._gcp_api_regions is None:
            raise ValueError("gcp_api_regions were not set")
        return self._gcp_api_regions

    @gcp_api_regions.setter
    def gcp_api_regions(self, value):
        if not isinstance(value, list):
            raise ValueError(
                f"gcp_api_regions must be a list received {value} of type: {type(value)}"
            )

        self._gcp_api_regions = value

    @property
    def accounts_file(self):
        return self._accounts_file

    @accounts_file.setter
    def accounts_file(self, value):
        self._accounts_file = value

    @property
    def gcp_account(self):
        if self._gcp_account is None:
            raise ValueError("gcp_account was not set")
        return self._gcp_account

    @gcp_account.setter
    def gcp_account(self, value):
        if not isinstance(value, str):
            raise ValueError(
                f"gcp_account must be a string received {value} of type: {type(value)}"
            )

        self._gcp_account = value

    @property
    def gcp_api_cache_dir(self):
        if self._gcp_api_cache_dir is None:
            raise ValueError("gcp_api_cache_dir was not set")
        return self._gcp_api_cache_dir

    @gcp_api_cache_dir.setter
    def gcp_api_cache_dir(self, value):
        self._gcp_api_cache_dir = value
        os.makedirs(self._gcp_api_cache_dir, exist_ok=True)
