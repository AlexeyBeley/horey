"""
Configuration policy used by Lion King project to set the configuration rules.

"""

import os
from horey.configuration_policy.configuration_policy import ConfigurationPolicy

#pylint: disable= missing-function-docstring

class LionKingConfigurationPolicy(ConfigurationPolicy):
    """
    Configuration policy implementation

    """
    def __init__(self):

        super().__init__()

        self._aws_api_configuration_file_full_path = None
        self._environment_name = None
        self._environment_level = None
        self._project_name = None
        self._region = None
        self._provision_infrastructure = None

    @property
    def aws_api_configuration_file_full_path(self):
        return self._aws_api_configuration_file_full_path

    @aws_api_configuration_file_full_path.setter
    def aws_api_configuration_file_full_path(self, value):
        self._aws_api_configuration_file_full_path = value

    @property
    def environment_name(self):
        return self._environment_name

    @environment_name.setter
    def environment_name(self, value):
        self._environment_name = value

    @property
    def environment_level(self):
        return self._environment_level

    @environment_level.setter
    def environment_level(self, value):
        self._environment_level = value

    @property
    def project_name(self):
        return self._project_name

    @project_name.setter
    def project_name(self, value):
        self._project_name = value

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, value):
        self._region = value

    @property
    def provision_infrastructure(self):
        return self._provision_infrastructure

    @provision_infrastructure.setter
    def provision_infrastructure(self, value):
        self._provision_infrastructure = value

    @property
    def vpc_cidr_block(self):
        return "10.0.0.0/21"

    @property
    def vpc_name(self):
        return f"vpc_{self.project_name}_{self.environment_name}"

    @property
    def availability_zones_count(self):
        return 3

    @property
    def subnet_mask_length(self):
        return 24

    @property
    def private_subnet_name_template(self):
        return f"subnet-private-{self.project_name}-{self.environment_name}-" + "{}"

    @property
    def public_subnet_name_template(self):
        return f"subnet-public-{self.project_name}-{self.environment_name}-" + "{}"

    @property
    def ecr_repository_name(self):
        return f"repo-{self.project_name}-{self.environment_name}"

    @property
    def infrastructure_last_update_time_tag(self):
        return "infra_update_datetime"

    @property
    def local_deployment_directory_path(self):
        return os.path.join(os.path.dirname(self.aws_api_configuration_file_full_path), "deployment")

    @property
    def db_rds_cluster_parameter_group_name(self):
        return f"cluster-param-grp-{self.project_name.replace('_', '-')}-{self.environment_name.replace('_', '-')}"

    @property
    def db_rds_cluster_parameter_group_description(self):
        return f"Database cluster parameter group {self.project_name} {self.environment_name}"

    @property
    def db_rds_instance_parameter_group_name(self):
        return f"instance-param-grp-{self.project_name.replace('_', '-')}-{self.environment_name.replace('_', '-')}"

    @property
    def db_rds_instance_id_template(self):
        return f"instance-{self.project_name}-{self.environment_name}-" + "{counter}"

    @property
    def db_rds_parameter_group_description(self):
        return f"Database instance parameter group {self.project_name} {self.environment_name}"

    @property
    def db_rds_subnet_group_name(self):
        return f"subnet-grp-{self.project_name.replace('_', '-')}-{self.environment_name.replace('_', '-')}"

    @property
    def db_rds_subnet_group_description(self):
        return f"Database subnet group {self.project_name} {self.environment_name}"

    @property
    def db_rds_cluster_identifier(self):
        return f"cluster-{self.project_name}-{self.environment_name}"

    @property
    def db_rds_database_name(self):
        return self.project_name

    @property
    def db_rds_security_group_name(self):
        return f"sg_postrgres-{self.project_name}-{self.environment_name}"

    @property
    def db_type(self):
        return "postgres"

    @property
    def db_instance_count(self):
        return 1

    @property
    def cluster_name(self):
        return f"cluster-{self.project_name}-{self.environment_name}"

    @property
    def ecs_task_definition_cpu_reservation(self):
        return 0.5

    @property
    def ecs_task_definition_memory_reservation(self):
        return 512

    @property
    def ecs_task_role_name(self):
        return f"role_{self.environment_name}_{self.project_name}-backend-task"

    @property
    def ecs_task_execution_role_name(self):
        return f"role_{self.environment_name}_{self.project_name}-backend-task-execution"
