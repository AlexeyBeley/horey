import os
from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class GoogleAPIConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._google_api_regions = None
        self._accounts_file = None
        self._google_api_account = None
        self._google_api_cache_dir = None

    @property
    def google_api_regions(self):
        if self._google_api_regions is None:
            raise ValueError("google_api_regions were not set")
        return self._google_api_regions

    @google_api_regions.setter
    def google_api_regions(self, value):
        if not isinstance(value, list):
            raise ValueError(
                f"google_api_regions must be a list received {value} of type: {type(value)}"
            )

        self._google_api_regions = value

    @property
    def accounts_file(self):
        return self._accounts_file

    @accounts_file.setter
    def accounts_file(self, value):
        self._accounts_file = value

    @property
    def google_api_account(self):
        if self._google_api_account is None:
            raise ValueError("google_api_account was not set")
        return self._google_api_account

    @google_api_account.setter
    def google_api_account(self, value):
        if not isinstance(value, str):
            raise ValueError(
                f"google_api_account must be a string received {value} of type: {type(value)}"
            )

        self._google_api_account = value

    @property
    def google_api_cache_dir(self):
        if self._google_api_cache_dir is None:
            raise ValueError("google_api_cache_dir was not set")
        return self._google_api_cache_dir

    @google_api_cache_dir.setter
    def google_api_cache_dir(self, value):
        self._google_api_cache_dir = value
        os.makedirs(self._google_api_cache_dir, exist_ok=True)
