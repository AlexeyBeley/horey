"""
Configuration policy used by Lion King project to set the configuration rules.

"""

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
    def vpc_cidr_block(self):
        return "10.0.0.0/22"

    @property
    def vpc_name(self):
        return f"vpc_{self.project_name}_{self.environment_name}"

    @property
    def availability_zones_count(self):
        return 2

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
