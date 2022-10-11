"""
HiBob API Configuration policy
"""
import os
from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable=missing-function-docstring


class BobAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class
    """

    def __init__(self):
        self._server_address = None
        self._token = None
        self._cache_dir_path = None

        super().__init__()

    @property
    def server_address(self):
        if self._server_address is None:
            raise ValueError("server_address was not set")
        return self._server_address

    @server_address.setter
    def server_address(self, value):
        """
        https://127.0.0.1
        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(f"server_address must be string received {value} of type: {type(value)}")

        self._server_address = value

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        if not isinstance(value, str) and value is not None:
            raise ValueError(f"token must be string or None received {value} of type: {type(value)}")

        self._token = value

    @property
    def cache_dir_path(self):
        return self._cache_dir_path

    @cache_dir_path.setter
    def cache_dir_path(self, value):
        self._cache_dir_path = value

    @property
    def employees_cache_file_path(self):
        return os.path.join(self.cache_dir_path, "employees_cache_file.json")
