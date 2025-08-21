"""
DB API config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


class DBAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._cluster_name = None
        self._engine_type = None
        self._cluster_parameter_group_name = None
        self._instance_parameter_group_name = None
        self._subnet_group_name = None
        self._backup_retention_days = None
        self._database_name = None
        self._security_group_names = None
        self._master_username = None
        self._deletion_protection = None
        self._serverless_v2_scaling_configuration = None
        self._db_instance_count = None
        self._instance_name_format = None

    @property
    def cluster_instance_class(self):
        return "db.serverless"

    @property
    def instance_name_format(self):
        if self._instance_name_format is None:
            self._instance_name_format = f"instance-{self.cluster_name}-" + "{id}"
        return self._instance_name_format

    @instance_name_format.setter
    def instance_name_format(self, value):
        self._instance_name_format = value

    @property
    def db_instance_count(self):
        if self._db_instance_count is None:
            self._db_instance_count = 1 
        return self._db_instance_count

    @db_instance_count.setter
    def db_instance_count(self, value):
        self._db_instance_count = value

    @property
    def serverless_v2_scaling_configuration(self):
        if self._serverless_v2_scaling_configuration is None:
            self._serverless_v2_scaling_configuration = {
            "MinCapacity": 1.0,
            "MaxCapacity": 3.0
        }
        return self._serverless_v2_scaling_configuration

    @serverless_v2_scaling_configuration.setter
    def serverless_v2_scaling_configuration(self, value):
        self._serverless_v2_scaling_configuration = value

    @property
    def deletion_protection(self):
        if self._deletion_protection is None:
            self._deletion_protection = False
        return self._deletion_protection

    @deletion_protection.setter
    def deletion_protection(self, value):
        self._deletion_protection = value

    @property
    def master_username(self):
        if self._master_username is None:
            self._master_username = "master"
        return self._master_username

    @master_username.setter
    def master_username(self, value):
        self._master_username = value

    @property
    def security_group_names(self):
        if self._security_group_names is None:
            raise self.UndefinedValueError("security_group_names")
        return self._security_group_names

    @security_group_names.setter
    def security_group_names(self, value):
        self._security_group_names = value

    @property
    def database_name(self):
        if self._database_name is None:
            raise self.UndefinedValueError("database_name")
        return self._database_name

    @database_name.setter
    def database_name(self, value):
        self._database_name = value

    @property
    def backup_retention_days(self):
        if self._backup_retention_days is None:
            self._backup_retention_days = 7 
        return self._backup_retention_days

    @backup_retention_days.setter
    def backup_retention_days(self, value):
        self._backup_retention_days = value

    @property
    def subnet_group_name(self):
        if self._subnet_group_name is None:
            self._subnet_group_name = f"subnet-group-{self.cluster_name}"
        return self._subnet_group_name

    @subnet_group_name.setter
    def subnet_group_name(self, value):
        self._subnet_group_name = value

    @property
    def instance_parameter_group_name(self):
        if self._instance_parameter_group_name is None:
            self._instance_parameter_group_name = f"param-group-instance-{self.cluster_name}"
        return self._instance_parameter_group_name

    @instance_parameter_group_name.setter
    def instance_parameter_group_name(self, value):
        self._instance_parameter_group_name = value

    @property
    def cluster_parameter_group_name(self):
        if self._cluster_parameter_group_name is None:
            self._cluster_parameter_group_name = f"param-group-cluster-{self.cluster_name}"
        return self._cluster_parameter_group_name

    @cluster_parameter_group_name.setter
    def cluster_parameter_group_name(self, value):
        self._cluster_parameter_group_name = value

    @property
    def engine_type(self):
        if self._engine_type is None:
            raise self.UndefinedValueError("engine_type")
        return self._engine_type

    @engine_type.setter
    def engine_type(self, value):
        self._engine_type = value

    @property
    def cluster_name(self):
        return self._cluster_name

    @cluster_name.setter
    def cluster_name(self, value):
        self._cluster_name = value

