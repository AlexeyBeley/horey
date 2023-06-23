"""
Configs
"""
from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring


class AzureDevopsAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class
    password is actually PAT: personal access token.

    Sign in to your organization (https://dev.azure.com/{yourorganization}).
    From your home page, open "user settings" and select Personal access tokens.
    Select + New Token.
    Name your token, select the organization where you want to use the token, and then set your token to automatically
     expire after a set number of days.
    Select the scopes for this token to authorize for your specific tasks.
    Presse "Create"
    When you're done, copy the token and store it in a secure location. For your security, it won't be shown again.

    https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Windows
    """
    def __init__(self):
        self._server_address = None
        self._user = None
        self._password = None
        self._org_name = None
        self._project_name = None
        self._team_name = None
        self._cache_dir_full_path = None

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
    
    @property
    def cache_dir_full_path(self):
        if self._cache_dir_full_path is None:
            raise ValueError("cache_dir_full_path was not set")
        return self._cache_dir_full_path

    @cache_dir_full_path.setter
    def cache_dir_full_path(self, value):
        """
        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(
                f"cache_dir_full_path must be string received {value} of type: {type(value)}"
            )

        self._cache_dir_full_path = value
