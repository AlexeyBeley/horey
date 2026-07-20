from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class SnykAPIConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        self._api_key = None
        self._org_id = None

        super().__init__()

    @property
    def api_key(self):
        if self._api_key is None:
            raise ValueError("api_key was not set")
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        """
        http://127.0.0.1:3000
        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(
                f"api_key must be string received {value} of type: {type(value)}"
            )

        self._api_key = value

    @property
    def org_id(self):
        if self._org_id is None:
            raise ValueError("org_id was not set")
        return self._org_id

    @org_id.setter
    def org_id(self, value):
        if not isinstance(value, str):
            raise ValueError(
                f"org_id must be string received {value} of type: {type(value)}"
            )

        self._org_id = value
