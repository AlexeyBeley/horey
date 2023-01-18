"""
Kapacitor configs.

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable=missing-function-docstring


class KapacitorAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class.

    """

    def __init__(self):
        self._server_address = None

        super().__init__()

    @property
    def server_address(self):
        if self._server_address is None:
            raise ValueError("server_address was not set")
        return self._server_address

    @server_address.setter
    def server_address(self, value):
        """
        http://127.0.0.1:9092
        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(
                f"server_address must be string received {value} of type: {type(value)}"
            )

        self._server_address = value
