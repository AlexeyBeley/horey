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
        self._lowest_domain_label = None

    @property
    def lowest_domain_label(self):
        if self._lowest_domain_label is None:
            if self._dns_address is None:
                raise self.UndefinedValueError("lowest_domain_label")
            self._lowest_domain_label = self._dns_address.split(".")[0]

        return self._lowest_domain_label

    @lowest_domain_label.setter
    def lowest_domain_label(self, value):
        self._lowest_domain_label = value

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
            if self._lowest_domain_label is None or self._hosted_zone_name is None:
                raise self.UndefinedValueError("dns_address")
            self._dns_address = f"{self._lowest_domain_label}.{self.hosted_zone_name}"
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

