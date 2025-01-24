"""
AWS ECS config

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring, too-many-instance-attributes


class ECSAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._load_balancer_target_group_arn = None
        self._container_ports = None
        self._ecr_repository_name = None
        self._ecr_repository_region = None
        self._infrastructure_update_time_tag = None
        self._ecr_repository_policy_text = None
        self._service_name = None
        self._cluster_name = None

    @property
    def cluster_name(self):
        if self._cluster_name is None:
            raise self.UndefinedValueError("cluster_name")
        return self._cluster_name

    @cluster_name.setter
    def cluster_name(self, value):
        self._cluster_name = value

    @property
    def service_name(self):
        if self._service_name is None:
            raise self.UndefinedValueError("service_name")
        return self._service_name

    @service_name.setter
    def service_name(self, value):
        self._service_name = value

    @property
    def ecr_repository_policy_text(self):
        # todo: cleanup report It is recommended to use resource policy on ecr repos.
        return self._ecr_repository_policy_text

    @ecr_repository_policy_text.setter
    def ecr_repository_policy_text(self, value):
        self._ecr_repository_policy_text = value

    @property
    def infrastructure_update_time_tag(self):
        if self._infrastructure_update_time_tag is None:
            self._infrastructure_update_time_tag = "update_time"
        return self._infrastructure_update_time_tag

    @infrastructure_update_time_tag.setter
    def infrastructure_update_time_tag(self, value):
        self._infrastructure_update_time_tag = value

    @property
    def ecr_repository_region(self):
        if self._ecr_repository_region is None:
            raise self.UndefinedValueError("ecr_repository_region")
        return self._ecr_repository_region

    @ecr_repository_region.setter
    def ecr_repository_region(self, value):
        self._ecr_repository_region = value

    @property
    def ecr_repository_name(self):
        if self._ecr_repository_name is None:
            self._ecr_repository_name = f"repo_{self.cluster_name}_{self.service_name}"
        return self._ecr_repository_name

    @ecr_repository_name.setter
    def ecr_repository_name(self, value):
        self._ecr_repository_name = value

    @property
    def container_ports(self):
        if self._container_ports is None:
            raise self.UndefinedValueError("container_ports")
        return self._container_ports

    @container_ports.setter
    def container_ports(self, value):
        self._container_ports = value

    @property
    def load_balancer_target_group_arn(self):
        if self._load_balancer_target_group_arn is None:
            raise self.UndefinedValueError("load_balancer_target_group_arn")
        return self._load_balancer_target_group_arn

    @load_balancer_target_group_arn.setter
    def load_balancer_target_group_arn(self, value):
        self._load_balancer_target_group_arn = value
