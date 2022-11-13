import os
from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class ElasticsearchAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Parameters:
        server: Base URI for elasticsearch web interface (omitting /api_jsonrpc.php)
        session: optional pre-configured requests.Session instance
        use_authenticate: Use old (Elasticsearch 1.8) style authentication
        timeout: optional connect and read timeout in seconds, default: None (if you're using Requests >= 2.4 you can set it as tuple: "(connect, read)" which is used to set individual connect and read timeouts.)
    """

    def __init__(self):
        self._server_address = None
        self._cache_dir = None
        super().__init__()

    @property
    def server_address(self):
        if self._server_address is None:
            raise ValueError("server_address was not set")
        return self._server_address

    @server_address.setter
    def server_address(self, value):
        if not isinstance(value, str):
            raise ValueError(
                f"server_address must be string received {value} of type: {type(value)}"
            )

        self._server_address = value

    @property
    def cache_dir(self):
        if self._cache_dir is None:
            raise ValueError("cache_dir was not set")
        return self._cache_dir

    @cache_dir.setter
    def cache_dir(self, value):
        if not isinstance(value, str):
            raise ValueError(
                f"cache_dir must be string received {value} of type: {type(value)}"
            )

        self._cache_dir = value
