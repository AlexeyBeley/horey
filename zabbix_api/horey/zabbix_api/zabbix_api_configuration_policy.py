import os
from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class ZabbixAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Parameters:
        server: Base URI for zabbix web interface (omitting /api_jsonrpc.php)
        session: optional pre-configured requests.Session instance
        use_authenticate: Use old (Zabbix 1.8) style authentication
        timeout: optional connect and read timeout in seconds, default: None (if you're using Requests >= 2.4 you can set it as tuple: "(connect, read)" which is used to set individual connect and read timeouts.)
    """

    def __init__(self):
        self._server = None
        self._server_address = None
        self._session = None
        self._user_authenticate = False
        self._token_authenticate = False
        self._username = None
        self._password = None
        self._timeout = None
        self._auth_token = None
        super().__init__()

    @property
    def server(self):
        if self._server is None:
            raise ValueError("server was not set")
        return self._server

    @server.setter
    def server(self, value):
        if not isinstance(value, str):
            raise ValueError(
                f"server must be string received {value} of type: {type(value)}"
            )

        self._server = value

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
    def url(self):
        return (
            self.server + "/api_jsonrpc.php"
            if not self.server.endswith("/api_jsonrpc.php")
            else self.server
        )

    @property
    def session(self):
        return self._session

    @property
    def user_authenticate(self):
        return self._user_authenticate

    @property
    def token_authenticate(self):
        return self._token_authenticate

    @token_authenticate.setter
    @ConfigurationPolicy.validate_type_decorator(bool)
    def token_authenticate(self, value):
        self._token_authenticate = value

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def timeout(self):
        return self._timeout

    @property
    def auth_token(self):
        return self._auth_token

    @auth_token.setter
    def auth_token(self, value):
        self._auth_token = value
