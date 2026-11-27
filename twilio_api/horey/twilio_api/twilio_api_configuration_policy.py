"""
Twilio API Configuration policy
"""
from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable=missing-function-docstring


class TwilioAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class
    """

    def __init__(self):
        self._account_sid = None
        self._token = None

        super().__init__()

    @property
    def account_sid(self):
        if self._account_sid is None:
            raise ValueError("account_sid was not set")
        return self._account_sid

    @account_sid.setter
    def account_sid(self, value):
        """
        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(
                f"account_sid must be string received {value} of type: {type(value)}"
            )

        self._account_sid = value

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
