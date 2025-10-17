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
        self._certificates_domain_names = None
        self._certificates_unmanaged_domain_names = []
        self._rule_priority = None
        self._rule_conditions = None
        self._target_type = None
        self._health_check_path = None
        self._target_group_targets = None
        self._target_group_port = None
        self._target_group_protocol = None
        self._listener_port = None

    @property
    def listener_port(self):
        if self._listener_port is None:
            return 443
        return self._listener_port

    @listener_port.setter
    def listener_port(self, value):
        self._listener_port = value

    @property
    def target_group_port(self):
        if self._target_group_port is None:
            return 443
        return self._target_group_port

    @target_group_port.setter
    def target_group_port(self, value):
        self._target_group_port = value

    @property
    def target_group_protocol(self):
        if self._target_group_protocol is None:
            return "HTTPS"
        return self._target_group_protocol

    @target_group_protocol.setter
    def target_group_protocol(self, value):
        if value not in ["HTTP", "HTTPS"]:
            raise ValueError(value)
        self._target_group_protocol = value

    @property
    def target_group_targets(self):
        return self._target_group_targets

    @target_group_targets.setter
    def target_group_targets(self, value):
        self._target_group_targets = value

    @property
    def health_check_path(self):
        if self._health_check_path is None:
            return "/health-check"
        return self._health_check_path

    @health_check_path.setter
    def health_check_path(self, value):
        self._health_check_path = value

    @property
    def target_type(self):
        if self._target_type is None:
            return "ip"
        return self._target_type

    @target_type.setter
    def target_type(self, value):
        self._target_type = value

    @property
    def rule_conditions(self):
        if self._rule_conditions is None:
            raise self.UndefinedValueError("rule_conditions")
        return self._rule_conditions

    @rule_conditions.setter
    def rule_conditions(self, value):
        self._rule_conditions = value

    @property
    def rule_priority(self):
        return self._rule_priority

    @rule_priority.setter
    def rule_priority(self, value):
        self._rule_priority = value

    @property
    def certificates_unmanaged_domain_names(self):
        return self._certificates_unmanaged_domain_names

    @certificates_unmanaged_domain_names.setter
    def certificates_unmanaged_domain_names(self, value):
        if not isinstance(value, list):
            raise ValueError(value)

        self._certificates_unmanaged_domain_names = value

    @property
    def certificates_domain_names(self):
        self.check_defined()
        return self._certificates_domain_names

    @certificates_domain_names.setter
    def certificates_domain_names(self, value):
        if not isinstance(value, list):
            raise ValueError(value)

        self._certificates_domain_names = value

    @property
    def target_group_name(self):
        self.check_defined()
        return self._target_group_name

    @target_group_name.setter
    def target_group_name(self, value):
        self._target_group_name = value

    @property
    def security_groups(self):
        self.check_defined()
        return self._security_groups

    @security_groups.setter
    def security_groups(self, value):
        self._security_groups = value

    @property
    def scheme(self):
        self.check_defined()
        return self._scheme

    @scheme.setter
    def scheme(self, value):
        assert value in ["internet-facing", "internal"]
        self._scheme = value

    @property
    def load_balancer_name(self):
        if self._load_balancer_name is None:
            raise self.UndefinedValueError("load_balancer_name")
        return self._load_balancer_name

    @load_balancer_name.setter
    def load_balancer_name(self, value):
        self._load_balancer_name = value
