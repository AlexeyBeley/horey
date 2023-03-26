"""
Configs
"""
from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring


class AzureDevopsAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class
    """
    def __init__(self):
        self._server_address = None
        self._user = None
        self._password = None
        self._org_name = None
        self._project_name = None
        self._team_name = None

        super().__init__()

    @property
    def server_address(self):
        if self._server_address is None:
            raise ValueError("server_address was not set")
        return self._server_address

    @server_address.setter
    def server_address(self, value):
        """
        http://127.0.0.1:8888
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
        """
        http://127.0.0.1:8888
        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(
                f"user must be string received {value} of type: {type(value)}"
            )

        self._user = value

    @property
    def password(self):
        if self._password is None:
            raise ValueError("password was not set")
        return self._password

    @password.setter
    def password(self, value):
        """
        http://127.0.0.1:8888
        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(
                f"password must be string received {value} of type: {type(value)}"
            )

        self._password = value

    @property
    def org_name(self):
        if self._org_name is None:
            raise ValueError("org_name was not set")
        return self._org_name

    @org_name.setter
    def org_name(self, value):
        """
        http://127.0.0.1:8888
        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(
                f"org_name must be string received {value} of type: {type(value)}"
            )

        self._org_name = value

    @property
    def team_name(self):
        if self._team_name is None:
            raise ValueError("team_name was not set")
        return self._team_name

    @team_name.setter
    def team_name(self, value):
        """
        http://127.0.0.1:8888
        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(
                f"team_name must be string received {value} of type: {type(value)}"
            )

        self._team_name = value

    @property
    def project_name(self):
        if self._project_name is None:
            raise ValueError("project_name was not set")
        return self._project_name

    @project_name.setter
    def project_name(self, value):
        """
        http://127.0.0.1:8888
        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(
                f"project_name must be string received {value} of type: {type(value)}"
            )

        self._project_name = value
