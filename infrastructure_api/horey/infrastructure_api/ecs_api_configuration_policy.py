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
        self._buildargs = None
        self._family = None
        self._container_name = None
        self._ecr_image_id = None
        self._container_definition_port_mappings = None
        self._cloudwatch_log_group_name = None
        self._requires_compatibilities = None
        self._network_mode = None
        self._ecs_task_definition_cpu_reservation = None
        self._ecs_task_definition_memory_reservation = None
        self._ecs_task_role_name = None
        self._ecs_task_execution_role_name = None
        self._task_definition_cpu_architecture = None
        self._task_definition_volumes = None
        self._task_definition_mount_points = None
        self._task_definition_entry_point = None
        self._task_definition_desired_count = None
        self._launch_type = None
        self._security_groups = None
        self._kill_old_containers = None
        self._slug = None

        self._service_load_balancers = None

        self._autoscaling_cpu_policy_name = None
        self._autoscaling_cpu_target_value = None
        self._autoscaling_ram_policy_name = None
        self._autoscaling_ram_target_value = None
        self._autoscaling_min_capacity = None
        self._autoscaling_max_capacity = None
        self._lb_facing_security_group_name = None
        self._alerts_api_error_filter_text = None

    @property
    def alerts_api_error_filter_text(self):
        if self._alerts_api_error_filter_text is None:
            self._alerts_api_error_filter_text = '"[ERROR]"'
        return self._alerts_api_error_filter_text

    @alerts_api_error_filter_text.setter
    def alerts_api_error_filter_text(self, value):
        self._alerts_api_error_filter_text = value

    @property
    def lb_facing_security_group_name(self):
        if self._lb_facing_security_group_name is None:
            self._lb_facing_security_group_name = f"sg_{self.cluster_name}_{self.service_name}"
        return self._lb_facing_security_group_name

    @lb_facing_security_group_name.setter
    def lb_facing_security_group_name(self, value):
        self._lb_facing_security_group_name = value

    @property
    def autoscaling_max_capacity(self):
        if self._autoscaling_max_capacity is None:
            raise self.UndefinedValueError("autoscaling_max_capacity")
        return self._autoscaling_max_capacity

    @autoscaling_max_capacity.setter
    def autoscaling_max_capacity(self, value):
        self._autoscaling_max_capacity = value

    @property
    def autoscaling_min_capacity(self):
        if self._autoscaling_min_capacity is None:
            raise self.UndefinedValueError("autoscaling_min_capacity")
        return self._autoscaling_min_capacity

    @autoscaling_min_capacity.setter
    def autoscaling_min_capacity(self, value):
        self._autoscaling_min_capacity = value

    @property
    def autoscaling_ram_target_value(self):
        if self._autoscaling_ram_target_value is None:
            self._autoscaling_ram_target_value = 80.0
        return self._autoscaling_ram_target_value

    @autoscaling_ram_target_value.setter
    def autoscaling_ram_target_value(self, value):
        self._autoscaling_ram_target_value = value

    @property
    def autoscaling_ram_policy_name(self):
        if self._autoscaling_ram_policy_name is None:
            self._autoscaling_ram_policy_name = f"aap-ram-{self.cluster_name}-{self.service_name}"
        return self._autoscaling_ram_policy_name

    @autoscaling_ram_policy_name.setter
    def autoscaling_ram_policy_name(self, value):
        self._autoscaling_ram_policy_name = value

    @property
    def autoscaling_cpu_target_value(self):
        if self._autoscaling_cpu_target_value is None:
            self._autoscaling_cpu_target_value = 80.0
        return self._autoscaling_cpu_target_value

    @autoscaling_cpu_target_value.setter
    def autoscaling_cpu_target_value(self, value):
        self._autoscaling_cpu_target_value = value

    @property
    def autoscaling_cpu_policy_name(self):
        if self._autoscaling_cpu_policy_name is None:
            self._autoscaling_cpu_policy_name = f"aap-cpu-{self.cluster_name}-{self.service_name}"
        return self._autoscaling_cpu_policy_name

    @autoscaling_cpu_policy_name.setter
    def autoscaling_cpu_policy_name(self, value):
        self._autoscaling_cpu_policy_name = value

    @property
    def slug(self):
        if self._slug is None:
            self._slug = f"{self.cluster_name.replace('cluster_', '')}-{self.service_name.replace('service_', '')}"
        return self._slug

    @property
    def service_load_balancers(self):
        if self._service_load_balancers is None:
            raise self.UndefinedValueError("service_load_balancers")
        return self._service_load_balancers

    @service_load_balancers.setter
    def service_load_balancers(self, value):
        self._service_load_balancers = value

    @property
    def kill_old_containers(self):
        if self._kill_old_containers is None:
            raise self.UndefinedValueError("kill_old_containers")
        return self._kill_old_containers

    @kill_old_containers.setter
    def kill_old_containers(self, value):
        self._kill_old_containers = value

    @property
    def security_groups(self):
        if self._security_groups is None:
            raise self.UndefinedValueError("security_groups")
        return self._security_groups

    @security_groups.setter
    def security_groups(self, value):
        self._security_groups = value

    @property
    def launch_type(self):
        if self._launch_type is None:
            self._launch_type = "FARGATE"
        return self._launch_type

    @launch_type.setter
    def launch_type(self, value):
        self._launch_type = value

    @property
    def task_definition_desired_count(self):
        if self._task_definition_desired_count is None:
            raise self.UndefinedValueError("task_definition_desired_count")
        return self._task_definition_desired_count

    @task_definition_desired_count.setter
    def task_definition_desired_count(self, value):
        self._task_definition_desired_count = value

    @property
    def task_definition_entry_point(self):
        return self._task_definition_entry_point

    @task_definition_entry_point.setter
    def task_definition_entry_point(self, value):
        self._task_definition_entry_point = value

    @property
    def task_definition_mount_points(self):
        return self._task_definition_mount_points

    @task_definition_mount_points.setter
    def task_definition_mount_points(self, value):
        self._task_definition_mount_points = value

    @property
    def task_definition_volumes(self):
        return self._task_definition_volumes

    @task_definition_volumes.setter
    def task_definition_volumes(self, value):
        self._task_definition_volumes = value

    @property
    def task_definition_cpu_architecture(self):
        if self._task_definition_cpu_architecture is None:
            raise self.UndefinedValueError("task_definition_cpu_architecture")
        return self._task_definition_cpu_architecture

    @task_definition_cpu_architecture.setter
    def task_definition_cpu_architecture(self, value):
        self._task_definition_cpu_architecture = value

    @property
    def ecs_task_execution_role_name(self):
        if self._ecs_task_execution_role_name is None:
            raise self.UndefinedValueError("ecs_task_execution_role_name")
        return self._ecs_task_execution_role_name

    @ecs_task_execution_role_name.setter
    def ecs_task_execution_role_name(self, value):
        self._ecs_task_execution_role_name = value

    @property
    def ecs_task_role_name(self):
        if self._ecs_task_role_name is None:
            raise self.UndefinedValueError("ecs_task_role_name")
        return self._ecs_task_role_name

    @ecs_task_role_name.setter
    def ecs_task_role_name(self, value):
        self._ecs_task_role_name = value

    @property
    def ecs_task_definition_memory_reservation(self):
        if self._ecs_task_definition_memory_reservation is None:
            raise self.UndefinedValueError("ecs_task_definition_memory_reservation")
        return self._ecs_task_definition_memory_reservation

    @ecs_task_definition_memory_reservation.setter
    def ecs_task_definition_memory_reservation(self, value):
        self._ecs_task_definition_memory_reservation = value

    @property
    def ecs_task_definition_cpu_reservation(self):
        if self._ecs_task_definition_cpu_reservation is None:
            raise self.UndefinedValueError("ecs_task_definition_cpu_reservation")
        return self._ecs_task_definition_cpu_reservation

    @ecs_task_definition_cpu_reservation.setter
    def ecs_task_definition_cpu_reservation(self, value):
        self._ecs_task_definition_cpu_reservation = value

    @property
    def network_mode(self):
        if self._network_mode is None:
            self._network_mode = "awsvpc"
        return self._network_mode

    @network_mode.setter
    def network_mode(self, value):
        self._network_mode = value

    @property
    def requires_compatibilities(self):
        if self._requires_compatibilities is None:
            if self.launch_type == "FARGATE":
                self._requires_compatibilities = ["FARGATE"]
            else:
                raise self.UndefinedValueError("requires_compatibilities")

        return self._requires_compatibilities

    @requires_compatibilities.setter
    def requires_compatibilities(self, value):
        self._requires_compatibilities = value

    @property
    def cloudwatch_log_group_name(self):
        if self._cloudwatch_log_group_name is None:
            self._cloudwatch_log_group_name = f"/ecs/{self.cluster_name}/{self.service_name}"
        return self._cloudwatch_log_group_name

    @cloudwatch_log_group_name.setter
    def cloudwatch_log_group_name(self, value):
        self._cloudwatch_log_group_name = value

    @property
    def container_definition_port_mappings(self):
        return self._container_definition_port_mappings

    @container_definition_port_mappings.setter
    def container_definition_port_mappings(self, value):
        self._container_definition_port_mappings = value

    @property
    def ecr_image_id(self):
        if self._ecr_image_id is None:
            raise self.UndefinedValueError("ecr_image_id")
        return self._ecr_image_id

    @ecr_image_id.setter
    def ecr_image_id(self, value):
        self._ecr_image_id = value

    @property
    def container_name(self):
        if self._container_name is None:
            self._container_name = self.service_name
        return self._container_name

    @container_name.setter
    def container_name(self, value):
        self._container_name = value

    @property
    def family(self):
        if self._family is None:
            self._family = f"td_{self.cluster_name}_{self.service_name}"
        return self._family

    @family.setter
    def family(self, value):
        self._family = value

    @property
    def buildargs(self):
        return self._buildargs

    @buildargs.setter
    def buildargs(self, value):
        self._buildargs = value

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

    @property
    def auto_scaling_resource_id(self):
        return f"service/{self.cluster_name}/{self.service_name}"
