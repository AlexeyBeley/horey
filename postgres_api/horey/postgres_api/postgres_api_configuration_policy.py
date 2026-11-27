"""
Postgres API configuration policy
"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

#pylint: disable= missing-function-docstring


class PostgresAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class.

    """

    def __init__(self):
        super().__init__()
        self._host = "localhost"
        self._port = 5432
        self._database = None
        self._username = None
        self._password = None

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value

    @property
    def database(self):
        return self._database

    @database.setter
    def database(self, value):
        self._database = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value
