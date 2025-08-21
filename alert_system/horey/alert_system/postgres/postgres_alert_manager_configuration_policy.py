"""
Postgres Alert Manager configuration policy.

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable=missing-function-docstring


class PostgresAlertManagerConfigurationPolicy(ConfigurationPolicy):
    """
    Main class.
    """

    def __init__(self):
        super().__init__()
        self._cluster = None
        self._routing_tags = None

    @property
    def routing_tags(self):
        return self._routing_tags

    @routing_tags.setter
    def routing_tags(self, value):
        self._routing_tags = value

    @property
    def cluster(self):
        return self._cluster

    @cluster.setter
    def cluster(self, value):
        self._cluster = value
