"""
AWS Lambda config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


class CICDAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._build_environment_variable = None
        self._efs_master_security_group_name = None
        self._master_efs_access_point_name = None
        self._master_file_system_name = None

    @property
    def master_file_system_name(self):
        self.check_defined()
        return self._master_file_system_name

    @property
    def master_efs_access_point_name(self):
        self.check_defined()
        return self._master_efs_access_point_name

    @property
    def efs_master_security_group_name(self):
        self.check_defined()
        return self._efs_master_security_group_name

    @property
    def build_environment_variable(self):
        if self._build_environment_variable is None:
            raise self.UndefinedValueError("build_environment_variable")
        return self._build_environment_variable  

    @build_environment_variable.setter
    def build_environment_variable(self, value):
        self._build_environment_variable = value

