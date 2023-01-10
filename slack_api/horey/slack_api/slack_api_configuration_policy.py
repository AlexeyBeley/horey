"""
Slack API config.

"""

from enum import Enum
from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring


class SlackAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        self._webhook_url = None
        self._bearer_token = None

        super().__init__()

    @property
    def webhook_url(self):
        if self._webhook_url is None:
            raise ValueError("webhook_url was not set")
        return self._webhook_url

    @webhook_url.setter
    def webhook_url(self, value):
        if not isinstance(value, str):
            raise ValueError(
                f"webhook_url must be string received {value} of type: {type(value)}"
            )

        self._webhook_url = value

    @property
    def bearer_token(self):
        return self._bearer_token

    @bearer_token.setter
    def bearer_token(self, value):
        if not isinstance(value, str):
            raise ValueError(
                f"bearer_token must be string received {value} of type: {type(value)}"
            )

        self._bearer_token = value

    class Types(Enum):
        """
        Message types.

        """

        STABLE = 0
        WARNING = 1
        CRITICAL = 2
