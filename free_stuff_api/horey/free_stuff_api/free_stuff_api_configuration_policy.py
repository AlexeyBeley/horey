"""
FB configuration policy
"""
from pathlib import Path
from horey.configuration_policy.configuration_policy import ConfigurationPolicy

#pylint: disable= missing-function-docstring


class FreeStuffAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class.

    """
    def __init__(self):
        super().__init__()
        self._telegram_bot_token = None
        self._telegram_chat_id = None
        self._region = None
        self._horey_directory_path = None
        self._chromedriver_path = None
        self._chrome_path = None
        self._db_file_path = None
        self._architecture = None
        self._proxy = None
        self._mgmt_server_address = None
        self._mgmt_server_ssh_key_path = None
        self._mgmt_server_ssh_port = None

    @property
    def mgmt_server_ssh_port(self):
        return self._mgmt_server_ssh_port

    @mgmt_server_ssh_port.setter
    def mgmt_server_ssh_port(self, value: str):
        self._mgmt_server_ssh_port = value 

    @property
    def mgmt_server_ssh_key_path(self):
        return self._mgmt_server_ssh_key_path

    @mgmt_server_ssh_key_path.setter
    def mgmt_server_ssh_key_path(self, value: str):
        self._mgmt_server_ssh_key_path = value
     
    @property
    def mgmt_server_address(self):
        return self._mgmt_server_address

    @mgmt_server_address.setter
    def mgmt_server_address(self, value: str):
        self._mgmt_server_address = value
 
    @property
    def proxy(self):
        return self._proxy

    @proxy.setter
    def proxy(self, value: str):
        self._proxy = value

    @property
    def architecture(self):
        return self._architecture

    @architecture.setter
    def architecture(self, value: str):
        value = value.lower()
        assert value in ["amd64", "arm64"]
        self._architecture = value

    @property
    def db_file_path(self):
        return self._db_file_path

    @db_file_path.setter
    def db_file_path(self, value: Path):
        self._db_file_path = value

    @property
    def chromedriver_path(self):
        return self._chromedriver_path

    @chromedriver_path.setter
    def chromedriver_path(self, value: Path):
        self._chromedriver_path = value

    @property
    def chrome_path(self):
        return self._chrome_path

    @chrome_path.setter
    def chrome_path(self, value: Path):
        self._chrome_path = value

    @property
    def horey_directory_path(self):
        return self._horey_directory_path

    @horey_directory_path.setter
    def horey_directory_path(self, value: Path):
        self._horey_directory_path = value

    @property
    def region(self):
        self.check_defined()
        return self._region

    @region.setter
    def region(self, value):
        self._region = value

    @property
    def telegram_chat_id(self):
        return self._telegram_chat_id

    @telegram_chat_id.setter
    def telegram_chat_id(self, value):
        self._telegram_chat_id = value

    @property
    def telegram_bot_token(self):
        return self._telegram_bot_token

    @telegram_bot_token.setter
    def telegram_bot_token(self, value):
        self._telegram_bot_token = value
