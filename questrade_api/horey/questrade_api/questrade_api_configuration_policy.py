from pathlib import Path
from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class QuestradeAPIConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._token = None
        self._account = None
        self._api_server = None
        self._data_directory = None

    @property
    def db_file_path(self):
        return self.data_directory / "questrade.db"

    @property
    def data_directory(self):
        if self._data_directory is None:
            self._data_directory = Path("/opt/horey/questrade")
        return self._data_directory

    @data_directory.setter
    def data_directory(self, value):
        self._data_directory = value

    @property
    def api_server(self):
        return self._api_server

    @api_server.setter
    def api_server(self, value):
        self._api_server = value

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

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
