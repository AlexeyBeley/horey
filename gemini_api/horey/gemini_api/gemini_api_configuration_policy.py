from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class GeminiAPIConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        self._api_key = None

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
