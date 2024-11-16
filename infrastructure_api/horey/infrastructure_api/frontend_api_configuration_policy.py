"""
AWS Frontend config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


class FrontendAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._bucket_name = None
        self._cloudfront_distribution_name = None
        self._dns_address = None
        self._ip_set_name = None
        self._web_acl_name = None

    @property
    def web_acl_name(self):
        if self._web_acl_name is None:
            raise self.UndefinedValueError("web_acl_name")
        return self._web_acl_name

    @web_acl_name.setter
    def web_acl_name(self, value):
        self._web_acl_name = value

    @property
    def ip_set_name(self):
        if self._ip_set_name is None:
            raise self.UndefinedValueError("ip_set_name")
        return self._ip_set_name

    @ip_set_name.setter
    def ip_set_name(self, value):
        self._ip_set_name = value

    @property
    def dns_address(self):
        if self._dns_address is None:
            raise self.UndefinedValueError("dns_address")
        return self._dns_address

    @dns_address.setter
    def dns_address(self, value):
        self._dns_address = value

    @property
    def cloudfront_distribution_name(self):
        if self._cloudfront_distribution_name is None:
            raise self.UndefinedValueError("cloudfront_distribution_name")
        return self._cloudfront_distribution_name

    @cloudfront_distribution_name.setter
    def cloudfront_distribution_name(self, value):
        self._cloudfront_distribution_name = value

    @property
    def bucket_name(self):
        if self._bucket_name is None:
            raise self.UndefinedValueError("bucket_name")
        return self._bucket_name

    @bucket_name.setter
    def bucket_name(self, value):
        self._bucket_name = value
