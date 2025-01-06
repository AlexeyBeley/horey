"""
Standard ECS maintainer.

"""
import copy
import json
from datetime import datetime

from horey.h_logger import get_logger

from horey.aws_api.aws_services_entities.ecr_image import ECRImage
from horey.aws_api.aws_services_entities.ecr_repository import ECRRepository
from horey.aws_api.base_entities.region import Region

logger = get_logger()


class ECSAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api
        self._ecr_repository= None
        self._ecr_images = None

    @property
    def ecr_repository(self):
        if self._ecr_repository is None:
            self.environment_api.aws_api.ecr_client.clear_cache(ECRRepository)
            src_ecr_repositories = self.environment_api.aws_api.ecr_client.get_region_repositories(
                region=Region.get_region(self.configuration.ecr_repository_region),
                repository_names=[
                    self.configuration.ecr_repository_name])
            if len(src_ecr_repositories) != 1:
                raise RuntimeError(f"Can not find repository {self.configuration.ecr_repository_name}")
            self._ecr_repository = src_ecr_repositories[0]
        return self._ecr_repository

    @property
    def ecr_images(self):
        if self._ecr_images is None:
            self.environment_api.aws_api.ecr_client.clear_cache(ECRImage)
            self._ecr_images = self.environment_api.aws_api.ecr_client.get_repository_images(self.ecr_repository)
        return self._ecr_images

    def provision(self):
        """
        Provision ECS infrastructure.

        :return:
        """
        
        self.provision_ecr_repository()
        return True

    def update(self):
        """

        :return:
        """

        ecs_task_definition = self.provision_ecs_task_definition()

        return self.provision_ecs_service(ecs_task_definition)

    def provision_ecs_task_definition(self):
        """
        Provision task definition.

        :return:
        """

        task_definition = self.environment_api.provision_ecs_fargate_task_definition(
            task_definition_family=self.configuration.family,
            contaner_name=self.configuration.container_name,
            ecr_image_id=self.configuration.ecr_image_id,
            port_mappings=self.configuration.container_definition_port_mappings,
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
            task_definition_cpu_architecture=self.configuration.task_definition_cpu_architecture
            )
        return task_definition

    def provision_ecs_service(self, ecs_task_definition):
        """
        Provision component's ECS service.

        :return:
        """

        security_groups = self.environment_api.get_security_groups(self.configuration.security_groups)
        return self.environment_api.provision_ecs_service(self.configuration.cluster_name,
                                                          ecs_task_definition,
                                                          td_desired_count=self.configuration.task_definition_desired_count,
                                                          launch_type=self.configuration.launch_type,
                                                          network_configuration={
                                                              "awsvpcConfiguration": {
                                                                  "subnets": [subnet.id for subnet in
                                                                              self.environment_api.private_subnets],
                                                                  "securityGroups": [security_group.id for
                                                                                     security_group in
                                                                                     security_groups],
                                                                  "assignPublicIp": "DISABLED"
                                                              }
                                                          },
                                                          service_name=self.configuration.service_name,
                                                          container_name=self.configuration.container_name,
                                                          kill_old_containers=self.configuration.kill_old_containers,
                                                          load_balancers=self.configuration.service_load_balancers
                                                          )

    def provision_ecr_repository(self):
        """
        Create or update the ECR repo

        :return:
        """

        repo = ECRRepository({})
        repo.region = Region.get_region(self.configuration.ecr_repository_region)
        repo.name = self.configuration.ecr_repository_name
        repo.policy_text = self.configuration.ecr_repository_policy_text
        repo.tags = copy.deepcopy(self.environment_api.configuration.tags)
        repo.tags.append({
            "Key": "Name",
            "Value": repo.name
        })

        repo.tags.append({
            "Key": self.configuration.infrastructure_update_time_tag,
            "Value": datetime.now().strftime("%Y_%m_%d_%H_%M")
        })

        self.environment_api.aws_api.provision_ecr_repository(repo)
        return repo
