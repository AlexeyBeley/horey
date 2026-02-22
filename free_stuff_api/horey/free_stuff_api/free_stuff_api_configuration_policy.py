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

    @property
    def horey_directory_path(self):
        return self._horey_directory_path

    @horey_directory_path.setter
    def horey_directory_path(self, value: Path):
        self._horey_directory_path = value

    @property
    def region(self):
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
