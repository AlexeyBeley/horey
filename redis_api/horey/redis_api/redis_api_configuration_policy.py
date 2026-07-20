"""
Opensearch API Config policy.
"""
from horey.configuration_policy.configuration_policy import ConfigurationPolicy


# pylint: disable= missing-function-docstring
class RedisAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class.
    """
    def __init__(self):
        self._host = None
        self._port = None

        super().__init__()

    @property
    def host(self):
        if self._host is None:
            raise ValueError("host was not set")
        return self._host

    @host.setter
    def host(self, value):
        if not isinstance(value, str):
            raise ValueError(
                f"host must be string received {value} of type: {type(value)}"
            )

        self._host = value

    @property
    def port(self):
        if self._port is None:
            raise ValueError("port was not set")
        return self._port

    @port.setter
    def port(self, value):
        if not isinstance(value, str):
            raise ValueError(
                f"port must be string received {value} of type: {type(value)}"
            )

        self._port = value
