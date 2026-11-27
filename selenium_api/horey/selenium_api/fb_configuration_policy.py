"""
FB configuration policy
"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

#pylint: disable= missing-function-docstring


class FBConfigurationPolicy(ConfigurationPolicy):
    """
    Main class.

    """
    def __init__(self):
        super().__init__()
        self._username = None
        self._password = None

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value
