import os
from horey.configuration_policy.configuration_policy import ConfigurationPolicy
from enum import Enum

class SlackAPIConfigurationPolicy(ConfigurationPolicy):
    """
    """

    def __init__(self):
        self._server = None

        super().__init__()

    @property
    def server(self):
        if self._server is None:
            raise ValueError("server was not set")
        return self._server

    @server.setter
    def server(self, value):
        if not isinstance(value, str):
            raise ValueError(f"server must be string received {value} of type: {type(value)}")

        self._server = value
        
    class Types(Enum):
        STABLE = 0
        WARNING = 1
        CRITICAL = 2
