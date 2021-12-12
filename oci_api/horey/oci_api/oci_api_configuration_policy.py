import os
from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class OCIAPIConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._oci_api_regions = None
        self._accounts_file = None
        self._oci_account = None
        self._oci_api_cache_dir = None

    @property
    def oci_api_regions(self):
        if self._oci_api_regions is None:
            raise ValueError("oci_api_regions were not set")
        return self._oci_api_regions

    @oci_api_regions.setter
    def oci_api_regions(self, value):
        if not isinstance(value, list):
            raise ValueError(f"oci_api_regions must be a list received {value} of type: {type(value)}")

        self._oci_api_regions = value

    @property
    def accounts_file(self):
        return self._accounts_file

    @accounts_file.setter
    def accounts_file(self, value):
        self._accounts_file = value

    @property
    def oci_account(self):
        if self._oci_account is None:
            raise ValueError("oci_account was not set")
        return self._oci_account

    @oci_account.setter
    def oci_account(self, value):
        if not isinstance(value, str):
            raise ValueError(f"oci_account must be a string received {value} of type: {type(value)}")

        self._oci_account = value

    @property
    def oci_api_cache_dir(self):
        if self._oci_api_cache_dir is None:
            raise ValueError("oci_api_cache_dir was not set")
        return self._oci_api_cache_dir

    @oci_api_cache_dir.setter
    def oci_api_cache_dir(self, value):
        self._oci_api_cache_dir = value
        os.makedirs(self._oci_api_cache_dir, exist_ok=True)
