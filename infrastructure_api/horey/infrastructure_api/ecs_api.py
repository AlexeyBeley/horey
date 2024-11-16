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
        breakpoint()

        security_group = self.aws_api.get_security_group_by_vpc_and_name(self.vpc,
                                                                 self.scoutbees_aws_configuration.service_image_anomaly_detection_security_group_name)

        self.provision_ecs_service(ecs_task_definition,
                                   td_desired_count=2,
                                   launch_type="FARGATE",
                                   network_configuration={
                                       "awsvpcConfiguration": {
                                           "subnets": [subnet.id for subnet in self.select_subnets("private")],
                                           "securityGroups": [security_group.id],
                                           "assignPublicIp": "DISABLED"
                                       }
                                   }
                                   )

    def provision_ecs_task_definition(self):
        """
        Provision task definition.

        :return:
        """
        breakpoint()
        self.environment_api.provision_ecs_fargate_task_definition()

    def _provision_ecs_service(self, ecs_task_definition, service_registries_arn=None,
                               service_registries_container_port=None,
                               service_target_group_arn=None,
                               load_balancer_container_port=None,
                               role_arn=None, td_desired_count=1,
                               ecs_cluster=None,
                               service_name=None,
                               container_name=None,
                               launch_type="EC2",
                               network_configuration=None,
                               deployment_maximum_percent=200):
        """
        Provision component's ECS service.

        :param service_registries_container_port:
        :param load_balancer_container_port:
        :param ecs_task_definition:
        :param service_registries_arn:
        :param service_target_group_arn:
        :param role_arn:
        :param td_desired_count:
        :return:
        """

        container_name = container_name or self.NAME

        if ecs_cluster is None:
            ecs_cluster = self.find_ecs_cluster()

        ecs_service = ECSService({})
        ecs_service.name = service_name or self.configuration.ecs_service_name
        ecs_service.region = self.region

        ecs_service.network_configuration = network_configuration

        ecs_service.tags = [{key.lower(): value for key, value in dict_tag.items()} for dict_tag in self.tags]
        ecs_service.tags.append({
            "key": "Name",
            "value": ecs_service.name
        })

        ecs_service.cluster_arn = ecs_cluster.arn
        ecs_service.task_definition = ecs_task_definition.arn

        if service_target_group_arn is not None:
            if load_balancer_container_port is None:
                raise ValueError("load_balancer_container_port was not set while using service_target_group_arn")

            ecs_service.load_balancers = [{
                "targetGroupArn": service_target_group_arn,
                "containerName": container_name,
                "containerPort": load_balancer_container_port
            }]

        if service_registries_arn is not None:
            if service_registries_container_port is None:
                raise ValueError("service_registries_container_port was not set while using service_registries_arn")

            ecs_service.service_registries = [{
                "registryArn": service_registries_arn,
                "containerName": container_name,
                "containerPort": service_registries_container_port
            }]

        ecs_service.desired_count = td_desired_count

        ecs_service.launch_type = launch_type

        if role_arn is not None:
            ecs_service.role_arn = role_arn

        ecs_service.deployment_configuration = {
            "deploymentCircuitBreaker": {
                "enable": False,
                "rollback": False
            },
            "maximumPercent": deployment_maximum_percent,
            "minimumHealthyPercent": 100
        }
        if launch_type != "FARGATE":
            ecs_service.placement_strategy = [
                {
                    "type": "spread",
                    "field": "attribute:ecs.availability-zone"
                },
                {
                    "type": "spread",
                    "field": "instanceId"
                }
            ]
        ecs_service.health_check_grace_period_seconds = 10
        ecs_service.scheduling_strategy = "REPLICA"
        ecs_service.enable_ecs_managed_tags = False
        ecs_service.enable_execute_command = True

        wait_timeout = 10 * 60 if self.configuration.brutal_deployment else 20 * 60
        logger.info(f"Starting ECS service deployment with {wait_timeout=}")
        self.aws_api.provision_ecs_service(ecs_service, wait_timeout=wait_timeout)
