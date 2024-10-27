"""
AWS EnvironmentAPI config

"""
from copy import deepcopy

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring


class EnvironmentAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._region = None
        self._project_name = None
        self._vpc_name = None
        self._tags = None
        self._vpc_primary_subnet = None
        self._availability_zones_count = None
        self._subnet_mask_length = None
        self._subnet_name_template = None
        self._internet_gateway_name = None
        self._route_table_name_template = None
        self._container_instance_security_group_name = None
        self._container_instance_ssh_key_pair_name = None
        self._secrets_manager_region = None
        self._container_instance_launch_template_name = None
        self._ecs_cluster_name = None
        self._container_instance_role_name = None
        self._iam_path = None
        self._container_instance_profile_name = None
        self._container_instance_auto_scaling_group_name = None
        self._container_instance_auto_scaling_group_min_size = None
        self._container_instance_auto_scaling_group_max_size = None
        self._container_instance_capacity_provider_name = None
        self._data_directory_path = None

    @property
    def data_directory_path(self):
        if self._data_directory_path is None:
            raise self.UndefinedValueError("data_directory_path")
        return self._data_directory_path

    @data_directory_path.setter
    def data_directory_path(self, value):
        self._data_directory_path = value

    @property
    def container_instance_capacity_provider_name(self):
        if self._container_instance_capacity_provider_name is None:
            raise self.UndefinedValueError("container_instance_capacity_provider_name")
        return self._container_instance_capacity_provider_name

    @container_instance_capacity_provider_name.setter
    def container_instance_capacity_provider_name(self, value):
        self._container_instance_capacity_provider_name = value

    @property
    def container_instance_auto_scaling_group_max_size(self):
        if self._container_instance_auto_scaling_group_max_size is None:
            raise self.UndefinedValueError("container_instance_auto_scaling_group_max_size")
        return self._container_instance_auto_scaling_group_max_size

    @container_instance_auto_scaling_group_max_size.setter
    def container_instance_auto_scaling_group_max_size(self, value):
        self._container_instance_auto_scaling_group_max_size = value

    @property
    def container_instance_auto_scaling_group_min_size(self):
        if self._container_instance_auto_scaling_group_min_size is None:
            raise self.UndefinedValueError("container_instance_auto_scaling_group_min_size")
        return self._container_instance_auto_scaling_group_min_size

    @container_instance_auto_scaling_group_min_size.setter
    def container_instance_auto_scaling_group_min_size(self, value):
        self._container_instance_auto_scaling_group_min_size = value

    @property
    def container_instance_auto_scaling_group_name(self):
        if self._container_instance_auto_scaling_group_name is None:
            raise self.UndefinedValueError("container_instance_auto_scaling_group_name")
        return self._container_instance_auto_scaling_group_name

    @container_instance_auto_scaling_group_name.setter
    def container_instance_auto_scaling_group_name(self, value):
        self._container_instance_auto_scaling_group_name = value

    @property
    def container_instance_profile_name(self):
        if self._container_instance_profile_name is None:
            raise self.UndefinedValueError("container_instance_profile_name")
        return self._container_instance_profile_name

    @container_instance_profile_name.setter
    def container_instance_profile_name(self, value):
        self._container_instance_profile_name = value

    @property
    def iam_path(self):
        if self._iam_path is None:
            raise self.UndefinedValueError("iam_path")
        return self._iam_path

    @iam_path.setter
    def iam_path(self, value):
        self._iam_path = value

    @property
    def container_instance_role_name(self):
        if self._container_instance_role_name is None:
            raise self.UndefinedValueError("container_instance_role_name")
        return self._container_instance_role_name

    @container_instance_role_name.setter
    def container_instance_role_name(self, value):
        self._container_instance_role_name = value

    @property
    def ecs_cluster_name(self):
        if self._ecs_cluster_name is None:
            raise self.UndefinedValueError("ecs_cluster_name")
        return self._ecs_cluster_name

    @ecs_cluster_name.setter
    def ecs_cluster_name(self, value):
        self._ecs_cluster_name = value

    @property
    def container_instance_launch_template_name(self):
        if self._container_instance_launch_template_name is None:
            raise self.UndefinedValueError("container_instance_launch_template_name")
        return self._container_instance_launch_template_name

    @container_instance_launch_template_name.setter
    def container_instance_launch_template_name(self, value):
        self._container_instance_launch_template_name = value

    @property
    def secrets_manager_region(self):
        if self._secrets_manager_region is None:
            raise self.UndefinedValueError("secrets_manager_region")
        return self._secrets_manager_region

    @secrets_manager_region.setter
    def secrets_manager_region(self, value):
        self._secrets_manager_region = value

    @property
    def container_instance_ssh_key_pair_name(self):
        if self._container_instance_ssh_key_pair_name is None:
            raise self.UndefinedValueError("container_instance_ssh_key_pair_name")
        return self._container_instance_ssh_key_pair_name

    @container_instance_ssh_key_pair_name.setter
    def container_instance_ssh_key_pair_name(self, value):
        self._container_instance_ssh_key_pair_name = value

    @property
    def container_instance_security_group_name(self):
        if self._container_instance_security_group_name is None:
            raise self.UndefinedValueError("container_instance_security_group_name")
        return self._container_instance_security_group_name

    @container_instance_security_group_name.setter
    def container_instance_security_group_name(self, value):
        self._container_instance_security_group_name = value

    @property
    def route_table_name_template(self):
        if self._route_table_name_template is None:
            raise self.UndefinedValueError("route_table_name_template")
        return self._route_table_name_template

    @route_table_name_template.setter
    def route_table_name_template(self, value):
        self._route_table_name_template = value

    @property
    def internet_gateway_name(self):
        if self._internet_gateway_name is None:
            raise self.UndefinedValueError("internet_gateway_name")
        return self._internet_gateway_name

    @internet_gateway_name.setter
    def internet_gateway_name(self, value):
        self._internet_gateway_name = value

    @property
    def subnet_name_template(self):
        if self._subnet_name_template is None:
            raise self.UndefinedValueError("subnet_name_template")
        return self._subnet_name_template

    @subnet_name_template.setter
    def subnet_name_template(self, value):
        self._subnet_name_template = value

    @property
    def subnet_mask_length(self):
        if self._subnet_mask_length is None:
            raise self.UndefinedValueError("subnet_mask_length")
        return self._subnet_mask_length

    @subnet_mask_length.setter
    def subnet_mask_length(self, value):
        self._subnet_mask_length = value

    @property
    def availability_zones_count(self):
        if self._availability_zones_count is None:
            raise self.UndefinedValueError("availability_zones_count")
        return self._availability_zones_count

    @availability_zones_count.setter
    def availability_zones_count(self, value):
        self._availability_zones_count = value

    @property
    def vpc_primary_subnet(self):
        if self._vpc_primary_subnet is None:
            raise self.UndefinedValueError("vpc_primary_subnet")
        return self._vpc_primary_subnet

    @vpc_primary_subnet.setter
    def vpc_primary_subnet(self, value):
        self._vpc_primary_subnet = value

    @property
    def tags(self):
        if self._tags is None:
            raise self.UndefinedValueError("tags")
        return deepcopy(self._tags)

    @tags.setter
    def tags(self, value):
        self._tags = value

    @property
    def vpc_name(self):
        if self._vpc_name is None:
            raise self.UndefinedValueError("vpc_name")
        return self._vpc_name

    @vpc_name.setter
    def vpc_name(self, value):
        self._vpc_name = value

    @property
    def region(self):
        if self._region is None:
            raise self.UndefinedValueError("region")
        return self._region

    @region.setter
    def region(self, value):
        self._region = value

    @property
    def project_name(self):
        if self._project_name is None:
            raise self.UndefinedValueError("project_name")
        return self._project_name

    @project_name.setter
    def project_name(self, value):
        self._project_name = value
