"""
Jira API
"""
from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring


class JiraAPIConfigurationPolicy(ConfigurationPolicy):
    """"
    Main class
    """
    def __init__(self):
        self._server_address = None
        self._user = None
        self._token = None

        super().__init__()

    @property
    def server_address(self):
        if self._server_address is None:
            raise ValueError("server_address was not set")
        return self._server_address

    @server_address.setter
    def server_address(self, value):
        """
        http://127.0.0.1:3000
        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(
                f"server_address must be string received {value} of type: {type(value)}"
            )

        self._server_address = value

    @property
    def user(self):
        if self._user is None:
            raise ValueError("user was not set")
        return self._user

    @user.setter
    def user(self, value):
        if not isinstance(value, str):
            raise ValueError(
                f"user must be string received {value} of type: {type(value)}"
            )

        self._user = value

    @property
    def token(self):
        if self._token is None:
            raise ValueError("token was not set")
        return self._token

    @token.setter
    def token(self, value):
        if not isinstance(value, str):
            raise ValueError(
                f"token must be string received {value} of type: {type(value)}"
            )

        self._token = value
