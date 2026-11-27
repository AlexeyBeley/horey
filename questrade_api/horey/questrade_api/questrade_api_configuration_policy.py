from pathlib import Path
from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class QuestradeAPIConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._token = None
        self._account = None
        self._api_server = None
        self._data_directory = None
        self._user = None
        self._password = None
        self._db_file_path = None
        self._db_file_name = None
        self._historical_data_db_file_path = None
        self._historical_data_db_file_name = None

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def db_file_name(self):
        if self._db_file_name is None:
            # self._db_file_name = "questrade.db"
            self._db_file_name = "questrade_base.db"
        return self._db_file_name

    @db_file_name.setter
    def db_file_name(self, value):
        self._db_file_name = value
    
    @property
    def historical_data_db_file_name(self):
        if self._historical_data_db_file_name is None:
            self._historical_data_db_file_name = "questrade_historical_data.db"
        return self._historical_data_db_file_name 
        
    @property
    def historical_data_db_file_path(self):
        if self._historical_data_db_file_path is None:
            self._historical_data_db_file_path = self.data_directory / self.historical_data_db_file_name
        return self._historical_data_db_file_path

    @property
    def db_file_path(self):
        if self._db_file_path is None:
            self._db_file_path = self.data_directory / self.db_file_name
        return self._db_file_path

    @db_file_path.setter
    def db_file_path(self, value):
        self._db_file_path = value

    @property
    def data_directory(self):
        if self._data_directory is None:
            self._data_directory = Path("/opt/horey/questrade")
        return self._data_directory

    @data_directory.setter
    def data_directory(self, value):
        self._data_directory = value

    @property
    def purchase_plan_file_path(self):
        return self.data_directory / "purchase_plan.json"

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

    @property
    def max_trading_value(self):
        return 10.0

    @property
    def min_trading_value(self):
        return  0.001
