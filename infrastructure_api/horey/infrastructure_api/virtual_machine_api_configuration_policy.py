"""
AWS IAM config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy


# pylint: disable= missing-function-docstring, too-many-instance-attributes


class VirtualMachineAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._name = None
        self._role_name = None
        self._profile_name = None
        self._environment_level = None
        self._environment_name = None
        self._seed = None
        self._project_name = None
        self._project_name_abbr = None
        self._ssh_key_pair_name = None
        self._security_group_name = None
        self._instance_type = None
        self._private = None
        self._volume_size = None

    @property
    def volume_size(self):
        if self._volume_size is None:
            return 30
        return self._volume_size

    @volume_size.setter
    def volume_size(self, value):
        self._volume_size = value

    @property
    def private(self):
        if self._private is None:
            return True 
        return self._private

    @private.setter
    def private(self, value):
        self._private = value

    @property
    def instance_type(self):
        if self._instance_type is None:
            return "t4g.small"
        return self._instance_type

    @instance_type.setter
    def instance_type(self, value):
        self._instance_type = value

    @property
    def security_group_name(self):
        if self._security_group_name is None:
            return f"sg_{self.seed}"
        return self._security_group_name

    @security_group_name.setter
    def security_group_name(self, value):
        self._security_group_name = value

    @property
    def ssh_key_pair_name(self):
        if self._ssh_key_pair_name is None:
            return f"key_pair_{self.seed}"
        return self._ssh_key_pair_name

    @ssh_key_pair_name.setter
    def ssh_key_pair_name(self, value):
        self._ssh_key_pair_name = value

    @property
    def name(self):
        if self._name is None:
            raise self.UndefinedValueError("name")
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def project_name_abbr(self):
        if self._project_name_abbr is None:
            raise self.UndefinedValueError("project_name_abbr")
        return self._project_name_abbr

    @project_name_abbr.setter
    def project_name_abbr(self, value):
        self._project_name_abbr = value

    @property
    def project_name(self):
        if self._project_name is None:
            raise self.UndefinedValueError("project_name")
        return self._project_name

    @project_name.setter
    def project_name(self, value):
        self._project_name = value

    @property
    def seed(self):
        if self._seed is None:
            return f"{self.project_name_abbr}_{self.environment_name}_{self.name}"
        return self._seed

    @seed.setter
    def seed(self, value):
        self._seed = value

    @property
    def environment_name(self):
        if self._environment_name is None:
            raise self.UndefinedValueError("environment_name")
        return self._environment_name

    @environment_name.setter
    def environment_name(self, value):
        self._environment_name = value

    @property
    def environment_level(self):
        if self._environment_level is None:
            raise self.UndefinedValueError("environment_level")
        return self._environment_level

    @environment_level.setter
    def environment_level(self, value):
        self._environment_level = value

    @property
    def profile_name(self):
        if self._profile_name is None:
            return f"profile_{self.seed}"
        return self._profile_name

    @profile_name.setter
    def profile_name(self, value):
        self._profile_name = value

    @property
    def role_name(self):
        if self._role_name is None:
            return f"role_{self._environment_level}_{self.seed}"
        return self._role_name

    @role_name.setter
    def role_name(self, value):
        self._role_name = value
