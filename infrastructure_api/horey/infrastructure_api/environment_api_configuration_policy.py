"""
AWS EnvironmentAPI config

"""

from enum import Enum
from copy import deepcopy
from pathlib import Path

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


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
        self._nat_gateways_count = None
        self._nat_gateway_elastic_address_name_template = None
        self._nat_gateway_name_template = None
        self._public_hosted_zone_domain_name = None
        self._response_headers_policy_name = None
        self._s3_bucket_policy_statements = []
        self._build_id = []
        self._private_subnets = []
        self._public_subnets = []
        self._availability_zones = None
        self._environment_level = None
        self._environment_name = None
        self._project_name_abbr = None
        self._environment_name_abbr = None

    @property
    def environment_name_abbr(self):
        if self._environment_name_abbr is None:
            raise self.UndefinedValueError("environment_name_abbr")
        return self._environment_name_abbr

    @environment_name_abbr.setter
    def environment_name_abbr(self, value):
        self._environment_name_abbr = value

    @property
    def project_name_abbr(self):
        if self._project_name_abbr is None:
            raise self.UndefinedValueError("project_name_abbr")
        return self._project_name_abbr

    @project_name_abbr.setter
    def project_name_abbr(self, value):
        self._project_name_abbr = value

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
        self.check_defined()
        return self._environment_level

    @environment_level.setter
    def environment_level(self, value):
        ConfigurationPolicy.check_value_is_valid(value, [member.value for member in self.EnvironmentLevel.__members__.values()])
        self._environment_level = value

    @property
    def environment_level_abbr(self):
        if self.environment_level == self.EnvironmentLevel.DEVELOPMENT.value:
            return "dev"
        if self.environment_level == self.EnvironmentLevel.STAGING.value:
            return "stg"
        if self.environment_level == self.EnvironmentLevel.PRODUCTION.value:
            return "prd"
        raise ValueError(f"Unknown env level: {self.environment_level}")

    @property
    def availability_zones(self):
        self.check_defined()
        return self._availability_zones

    @availability_zones.setter
    @ConfigurationPolicy.validate_type_decorator(int)
    def availability_zones(self, value):
        self._availability_zones = value

    @property
    def public_subnets(self):
        if self._public_subnets is None:
            raise self.UndefinedValueError("public_subnets")
        return self._public_subnets

    @public_subnets.setter
    def public_subnets(self, value):
        self._public_subnets = value

    @property
    def private_subnets(self):
        if self._private_subnets is None:
            raise self.UndefinedValueError("private_subnets")
        return self._private_subnets

    @private_subnets.setter
    def private_subnets(self, value):
        self._private_subnets = value

    @property
    def build_id(self):
        if self._build_id is None:
            raise self.UndefinedValueError("build_id")
        return self._build_id

    @build_id.setter
    def build_id(self, value):
        self._build_id = value

    @property
    def s3_bucket_policy_statements(self):
        return self._s3_bucket_policy_statements

    @s3_bucket_policy_statements.setter
    def s3_bucket_policy_statements(self, value):
        self._s3_bucket_policy_statements = value

    @property
    def response_headers_policy_name(self):
        if self._response_headers_policy_name is None:
            raise self.UndefinedValueError("response_headers_policy_name")
        return self._response_headers_policy_name

    @response_headers_policy_name.setter
    def response_headers_policy_name(self, value):
        self._response_headers_policy_name = value

    @property
    def public_hosted_zone_domain_name(self):
        if self._public_hosted_zone_domain_name is None:
            raise self.UndefinedValueError("public_hosted_zone_domain_name")
        return self._public_hosted_zone_domain_name

    @public_hosted_zone_domain_name.setter
    def public_hosted_zone_domain_name(self, value):
        self._public_hosted_zone_domain_name = value

    @property
    def nat_gateway_name_template(self):
        if self._nat_gateway_name_template is None:
            raise self.UndefinedValueError("nat_gateway_name_template")
        return self._nat_gateway_name_template

    @nat_gateway_name_template.setter
    def nat_gateway_name_template(self, value):
        self._nat_gateway_name_template = value

    @property
    def nat_gateway_elastic_address_name_template(self):
        if self._nat_gateway_elastic_address_name_template is None:
            raise self.UndefinedValueError("nat_gateway_elastic_address_name_template")
        return self._nat_gateway_elastic_address_name_template

    @nat_gateway_elastic_address_name_template.setter
    def nat_gateway_elastic_address_name_template(self, value):
        self._nat_gateway_elastic_address_name_template = value

    @property
    def nat_gateways_count(self):
        if self._nat_gateways_count is None:
            raise self.UndefinedValueError("nat_gateways_count")
        return self._nat_gateways_count

    @nat_gateways_count.setter
    def nat_gateways_count(self, value):
        self._nat_gateways_count = value

    @property
    def data_directory_path(self):
        if self._data_directory_path is None:
            return Path("/opt") / self.project_name
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
            return f"/{self.environment_level}/"
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
            return self.region
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
            return f"subnet_{self.project_name_abbr}_{self.environment_name}_" + "{type}_{id}"
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
            return 3
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
            return [
                {
                    "Key": "env_level",
                    "Value": self.environment_level
                },
                {
                    "Key": "env_name",
                    "Value": self.environment_name
                },
                {
                    "Key": "region",
                    "Value": self.region
                },
                {
                    "Key": "project_name",
                    "Value": self.project_name
                }
            ]

        return deepcopy(self._tags)

    @tags.setter
    def tags(self, value):
        self._tags = value

    @property
    def vpc_name(self):
        if self._vpc_name is None:
            if self.environment_name == self.environment_level:
                return f"vpc-{self.project_name}-{self.environment_name}"

            return f"vpc-{self.project_name}-{self.environment_level}-{self.environment_name}"

        return self._vpc_name

    @vpc_name.setter
    def vpc_name(self, value):
        self._vpc_name = value

    @property
    def region(self):
        self.check_defined()
        return self._region

    @region.setter
    def region(self, value):
        self._region = value

    @property
    def project_name(self):
        self.check_defined()
        return self._project_name

    @project_name.setter
    def project_name(self, value):
        self._project_name = value

    class EnvironmentLevel(Enum):
        """
        Only these levels allowed.
        """

        PRODUCTION = "production"
        STAGING = "staging"
        DEVELOPMENT = "development"
