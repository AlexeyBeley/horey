from horey.configuration_policy.configuration_policy import ConfigurationPolicy
from enum import Enum


class SlackAPIConfigurationPolicy(ConfigurationPolicy):

    def __init__(self):
        self._webhook_url = None

        super().__init__()

    @property
    def webhook_url(self):
        if self._webhook_url is None:
            raise ValueError("webhook_url was not set")
        return self._webhook_url

    @webhook_url.setter
    def webhook_url(self, value):
        if not isinstance(value, str):
            raise ValueError(f"webhook_url must be string received {value} of type: {type(value)}")

        self._webhook_url = value
        
    class Types(Enum):
        STABLE = 0
        WARNING = 1
        CRITICAL = 2
