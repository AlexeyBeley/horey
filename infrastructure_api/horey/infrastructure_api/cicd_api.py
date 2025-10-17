"""
Standard Load balancing maintainer.

"""
import time

from horey.infrastructure_api.cloudwatch_api_configuration_policy import CloudwatchAPIConfigurationPolicy
from horey.infrastructure_api.cloudwatch_api import CloudwatchAPI
from horey.infrastructure_api.ecs_api import ECSAPI, ECSAPIConfigurationPolicy
from horey.infrastructure_api.cicd_api_configuration_policy import CICDAPIConfigurationPolicy
from horey.infrastructure_api.environment_api import EnvironmentAPI
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI
from horey.infrastructure_api.loadbalancer_api import LoadbalancerAPIConfigurationPolicy
from horey.infrastructure_api.dns_api import DNSAPIConfigurationPolicy


from horey.h_logger import get_logger

logger = get_logger()


class CICDAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration: CICDAPIConfigurationPolicy, environment_api: EnvironmentAPI):
        self.configuration = configuration
        self.environment_api = environment_api
        self._cloudwatch_api = None
        self.ecs_api = None
        self._dns_api = None

    @property
    def cloudwatch_api(self):
        """
        Standard.

        :return:
        """
        if self._cloudwatch_api is None:
            config = CloudwatchAPIConfigurationPolicy()
            self._cloudwatch_api = CloudwatchAPI(configuration=config, environment_api=self.environment_api)
        return self._cloudwatch_api

    def set_api(self, ecs_api=None, cloudwatch_api=None, dns_api=None):
        """
        Set apis.

        :param dns_api:
        :param cloudwatch_api:
        :param ecs_api:
        :return:
        """

        if ecs_api:
            self.ecs_api = ecs_api
            try:
                ecs_api.configuration.adhoc_task_name
            except ecs_api.configuration.UndefinedValueError:
                ecs_api.configuration.adhoc_task_name = "hagent"

        if cloudwatch_api:
            self._cloudwatch_api = cloudwatch_api

            try:
                self.cloudwatch_api.configuration.log_group_name
            except self._cloudwatch_api.configuration.UndefinedValueError:
                self.cloudwatch_api.configuration.log_group_name = ecs_api.configuration.cloudwatch_log_group_name

            self.ecs_api.set_api(cloudwatch_api=self.cloudwatch_api)

        if dns_api:
            self._dns_api = dns_api

    def provision(self):
        """
        Provision CICD infrastructure.

        :return:
        """

        self.provision_master_infrastructure()
        breakpoint()
        self.ecs_api.provision_ecs_task_definition(self.ecs_api.ecr_repo_uri + ":latest")
        self.cloudwatch_api.provision()

    def provision_master_infrastructure(self):
        """
        Jenkins Master infra

        :return:
        """
        self.ecs_api = self.generate_ecs_api()
        # todo: remove:
        self.ecs_api.update()

        self.ecs_api.provision()
        breakpoint()
        ecs_cluster = self.provision_ecs_cluster()
        self.provision_master_security_group()
        self.provision_master_ecr_repository()
        self.provision_master_alb_target_group(self.configuration.load_balancer_target_group_name)
        self.provision_master_cloudwatch_log_group()
        self.provision_master_ecs_task_execution_role()
        self.provision_master_ecs_task_role()

        self.provision_efs()

    def update(self):
        """

        :return:
        """
        perf_counter_start = time.perf_counter()
        overrides = {"containerOverrides": [{"name": self.ecs_api.configuration.container_name,
                                             "environment": [{"name": key, "value": value} for key, value in
                                                             self.configuration.build_environment_variable.items()]}]}

        task = self.ecs_api.start_task(overrides=overrides)
        response = self.ecs_api.wait_for_task_to_finish(task)
        logger.info(f"Time took from triggering task to its completion: {time.perf_counter()-perf_counter_start}")
        return response

    @property
    def loadbalancer_api(self):
        """
        Init load balancer api

        :return:
        """

        configuration = LoadbalancerAPIConfigurationPolicy()
        return InfrastructureAPI.get_loadbalancer_api(configuration, self.environment_api)

    @property
    def dns_api(self):
        """
        Init load balancer api

        :return:
        """
        if self._dns_api is None:
            configuration = DNSAPIConfigurationPolicy()
            return InfrastructureAPI.get_dns_api(configuration, self.environment_api)
        return self._dns_api

    def generate_ecs_api(self):
        """
        Generate environment config

        :return:
        """

        ecs_api_configuration = ECSAPIConfigurationPolicy()
        ecs_api_configuration.service_name = "jenkins"
        ecs_api = ECSAPI(ecs_api_configuration, self.environment_api)

        ecs_api_configuration.ecs_task_definition_cpu_reservation = 1024
        ecs_api_configuration.ecs_task_definition_memory_reservation = 2048
        ecs_api_configuration.autoscaling_max_capacity = 1
        ecs_api_configuration.network_mode = "awsvpc"

        ecs_api_configuration._container_definition_port_mappings = [
                {
                    "containerPort": 8080,
                    "hostPort": 0,
                    "protocol": "tcp",
                },
            ]

        ecs_api_configuration.task_definition_desired_count = 1
        ecs_api_configuration.launch_type = "FARGATE"
        ecs_api_configuration.kill_old_containers = False

        # todo:
        # ecs_api.environment_variables_callback = lambda: self.environment_api.async_orchestrator.get_task_result(
        #    self.async_task_id_generator(self.sync_generate_environment_variables), timeout = 2 * 60)
        ecs_api.set_api(loadbalancer_api=self.loadbalancer_api)
        ecs_api.set_api(dns_api=self.dns_api)
        return ecs_api
