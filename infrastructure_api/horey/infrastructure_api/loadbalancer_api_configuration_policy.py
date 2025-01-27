"""
AWS Lambda config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


class LoadbalancerAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._load_balancer_name = None
        self._scheme = None
        self._security_groups = None
        self._target_group_name = None
        self._public_domain_names = None
        self._unmanaged_public_domain_names = []

    @property
    def unmanaged_public_domain_names(self):
        return self._unmanaged_public_domain_names

    @unmanaged_public_domain_names.setter
    def unmanaged_public_domain_names(self, value):
        if not isinstance(value, list):
            raise ValueError(value)

        self._unmanaged_public_domain_names = value

    @property
    def public_domain_names(self):
        if self._public_domain_names is None:
            raise self.UndefinedValueError("public_domain_names")
        return self._public_domain_names

    @public_domain_names.setter
    def public_domain_names(self, value):
        if not isinstance(value, list):
            raise ValueError(value)

        self._public_domain_names = value

    @property
    def target_group_name(self):
        if self._target_group_name is None:
            raise self.UndefinedValueError("target_group_name")
        return self._target_group_name

    @target_group_name.setter
    def target_group_name(self, value):
        self._target_group_name = value

    @property
    def security_groups(self):
        if self._security_groups is None:
            raise self.UndefinedValueError("security_groups")
        return self._security_groups

    @security_groups.setter
    def security_groups(self, value):
        self._security_groups = value

    @property
    def scheme(self):
        if self._scheme is None:
            self._scheme = 30
        return self._scheme

    @scheme.setter
    def scheme(self, value):
        assert value in ["internet-facing"]
        self._scheme = value

    @property
    def load_balancer_name(self):
        if self._load_balancer_name is None:
            raise self.UndefinedValueError("load_balancer_name")
        return self._load_balancer_name

    @load_balancer_name.setter
    def load_balancer_name(self, value):
        self._load_balancer_name = value
