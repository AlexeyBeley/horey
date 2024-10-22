"""
Jenkins API configuration policy
"""
from horey.configuration_policy.configuration_policy import ConfigurationPolicy

#pylint: disable= missing-function-docstring


class JenkinsAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class.

    """
    def __init__(self):
        super().__init__()
        self._host = None
        self._username = None
        self._token = None
        self._timeout = None
        self._cache_dir_path = None
        self._region = "us-west-2"
        self._vpc_name = "horey_jenkins"
        self._vpc_primary_subnet = "192.168.0.0/24"

    @property
    def vpc_primary_subnet(self):
        return self._vpc_primary_subnet

    @vpc_primary_subnet.setter
    def vpc_primary_subnet(self, value):
        self._vpc_primary_subnet = value

    @property
    def vpc_name(self):
        return self._vpc_name

    @vpc_name.setter
    def vpc_name(self, value):
        self._vpc_name = value

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, value):
        self._region = value

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self._timeout = value

    @property
    def cache_dir_path(self):
        return self._cache_dir_path

    @cache_dir_path.setter
    def cache_dir_path(self, value):
        self._cache_dir_path = value
