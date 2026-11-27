from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class GitlabAPIConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        self._server_address = None
        self._group_id = None
        self._token_name = None
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
    def group_id(self):
        if self._group_id is None:
            raise ValueError("group_id was not set")
        return self._group_id

    @group_id.setter
    def group_id(self, value):
        if not isinstance(value, str):
            raise ValueError(
                f"group_id must be string received {value} of type: {type(value)}"
            )

        self._group_id = value

    @property
    def token_name(self):
        if self._token_name is None:
            raise ValueError("token_name was not set")
        return self._token_name

    @token_name.setter
    def token_name(self, value):
        if not isinstance(value, str):
            raise ValueError(
                f"token_name must be string received {value} of type: {type(value)}"
            )

        self._token_name = value

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        if not isinstance(value, str) and value is not None:
            raise ValueError(
                f"token must be string or None received {value} of type: {type(value)}"
            )

        self._token = value
