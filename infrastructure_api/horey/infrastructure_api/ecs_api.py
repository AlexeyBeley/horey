"""
Standard ECS maintainer.

"""
from horey.h_logger import get_logger

logger = get_logger()


class ECSAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api

    def provision(self):
        """
        Provision ECS infrastructure.

        :return:
        """

        return

    def update(self):
        """

        :return:
        """

        ecs_task_definition = self.provision_ecs_task_definition()

        self.provision_ecs_service(ecs_task_definition)

    def provision_ecs_task_definition(self):
        """
        Provision task definition.

        :return:
        """

        self.environment_api.provision_ecs_fargate_task_definition(task_definition_family=self.configuration.family,
                                                                   service_name=self.configuration.service_name,
                                                                   ecr_image_id=self.configuration.ecr_image_id,
                                                                   port_mappings=None,
                                                                   cloudwatch_log_group_name=self.configuration.cloudwatch_log_group_name,
                                                                   entry_point=None,
                                                                   environ_values=self.configuration.environ_values,
                                                                   requires_compatibilities=self.configuration.requires_compatibilities,
                                                                   network_mode=self.configuration.network_mode,
                                                                   volumes=None,
                                                                   mount_points=None,
                                                                   ecs_task_definition_cpu_reservation=self.configuration.ecs_task_definition_cpu_reservation,
                                                                   ecs_task_definition_memory_reservation=self.configuration.ecs_task_definition_memory_reservation,
                                                                   ecs_task_role_name=self.configuration.ecs_task_role_name,
                                                                   ecs_task_execution_role_name=self.configuration.ecs_task_execution_role_name,
                                                                   task_definition_cpu_architecture=self.configuration.task_definition_cpu_architecture)

    def provision_ecs_service(self, ecs_task_definition):
        """
        Provision component's ECS service.

        :return:
        """

        security_groups = self.environment_api.get_security_groups(self.configuration.security_groups)
        self.environment_api.provision_ecs_service(self.configuration.cluster_name,
                                                   ecs_task_definition,
                                                   td_desired_count=self.configuration.task_desired_count,
                                                   launch_type=self.configuration.launch_type,
                                                   network_configuration={
                                                       "awsvpcConfiguration": {
                                                           "subnets": [subnet.id for subnet in
                                                                       self.environment_api.private_subnets],
                                                           "securityGroups": [security_group.id for security_group in
                                                                              security_groups],
                                                           "assignPublicIp": "DISABLED"
                                                       }
                                                   },
                                                   service_name=self.configuration.service_name,
                                                   container_name=self.configuration.service_name,
                                                   kill_old_containers=self.configuration.kill_old_containers
                                                   )
