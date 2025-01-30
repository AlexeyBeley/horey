"""
AWS Lambda config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


class DNSAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._hosted_zone_name = None
        self._dns_address = None
        self._dns_target = None

    @property
    def dns_target(self):
        if self._dns_target is None:
            raise self.UndefinedValueError("dns_target")
        return self._dns_target

    @dns_target.setter
    def dns_target(self, value):
        self._dns_target = value

    @property
    def dns_address(self):
        if self._dns_address is None:
            raise self.UndefinedValueError("dns_address")
        return self._dns_address

    @dns_address.setter
    def dns_address(self, value):
        self._dns_address = value

    @property
    def hosted_zone_name(self):
        return self._hosted_zone_name

    @hosted_zone_name.setter
    def hosted_zone_name(self, value):
        self._hosted_zone_name = value

