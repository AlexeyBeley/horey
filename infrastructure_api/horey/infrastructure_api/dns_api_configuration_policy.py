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
        self._service_address = None

    @property
    def service_address(self):
        if self._service_address is None:
            raise self.UndefinedValueError("service_address")
        return self._service_address

    @service_address.setter
    def service_address(self, value):
        self._service_address = value

    @property
    def hosted_zone_name(self):
        if self._hosted_zone_name is None:
            raise self.UndefinedValueError("hosted_zone_name")
        return self._hosted_zone_name

    @hosted_zone_name.setter
    def hosted_zone_name(self, value):
        self._hosted_zone_name = value

