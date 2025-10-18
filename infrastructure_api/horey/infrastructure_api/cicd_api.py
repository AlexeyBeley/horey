"""
Standard Load balancing maintainer.

"""
import pathlib
import time
import getpass

from horey.infrastructure_api.cloudwatch_api_configuration_policy import CloudwatchAPIConfigurationPolicy
from horey.infrastructure_api.cloudwatch_api import CloudwatchAPI
from horey.infrastructure_api.ecs_api import ECSAPI, ECSAPIConfigurationPolicy
from horey.infrastructure_api.cicd_api_configuration_policy import CICDAPIConfigurationPolicy
from horey.infrastructure_api.environment_api import EnvironmentAPI
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI
from horey.infrastructure_api.loadbalancer_api import LoadbalancerAPIConfigurationPolicy
from horey.infrastructure_api.dns_api import DNSAPIConfigurationPolicy
from horey.git_api.git_api import GitAPI, GitAPIConfigurationPolicy
from horey.aws_api.aws_clients.efs_client import EFSFileSystem, EFSAccessPoint, EFSMountTarget


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

        self.configuration._efs_master_security_group_name = f"sg_{self.environment_api.configuration.environment_level}" \
                                                             f"-{self.environment_api.configuration.environment_name}" \
                                                             f"-jenkins"

        self.configuration._master_efs_access_point_name = f"acp_{self.environment_api.configuration.environment_level}" \
                                                             f"-{self.environment_api.configuration.environment_name}" \
                                                             f"-jenkins"

        self.configuration._master_file_system_name = f"fs_{self.environment_api.configuration.environment_level}" \
                                                             f"-{self.environment_api.configuration.environment_name}" \
                                                             f"-jenkins"

        self.ecs_api = self.generate_ecs_api()
        self.provision_efs()
        # todo: remove:
        self.ecs_api.update()
        breakpoint()

        self.ecs_api.provision()

    def update(self):
        """
        aws ecs execute-command --region us-east-1 --cluster cluster-sb-production-management --task 97e87487c0a74421ab53c2fed0a726cc  --container  sb-production-management-jenkins --command "/bin/sh" --interactive
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

    def provision_efs(self):
        """
        Standard.
        --volume jenkins-data:/var/jenkins_home

        :return:
        """

        efs_security_group = self.provision_efs_security_group()
        master_efs = self.provision_master_efs_file_system()
        pgadmin_access_point = self.provision_master_efs_access_point(master_efs.id)
        self.provision_efs_mount_targets(master_efs.id, efs_security_group.id)
        volumes, mount_points = self.generate_volume_and_mount_configuration(master_efs, pgadmin_access_point,
                                                                             "/var/jenkins_home")
        self.ecs_api.configuration.task_definition_volumes = volumes
        self.ecs_api.configuration.task_definition_mount_points = mount_points

    @staticmethod
    def generate_volume_and_mount_configuration(efs, access_point, container_path):
        """
        Generates the EFS volume and mount point configurations for the ECS task definition.

        :param efs:
        :param access_point:
        :param container_path: Path inside the container where the EFS volume will be mounted.
        :return: ecs task volumes configuration, ecs task mount_points configuration.

        """

        volume_name = efs.name
        volumes = [{
            "name": volume_name,
            "efsVolumeConfiguration": {
                "fileSystemId": efs.id,
                "transitEncryption": "ENABLED",
                "authorizationConfig": {
                    "accessPointId": access_point.id,
                    "iam": "ENABLED"
                }
            }
        }]

        mount_points = [{
            "sourceVolume": volume_name,
            "containerPath": container_path,
            "readOnly": False
        }]

        return volumes, mount_points

    def provision_efs_security_group(self):
        """
        Provision pgadmin efs  security group.

        :return:
        """

        jenkins_master = self.environment_api.get_security_groups([self.ecs_api.configuration.lb_facing_security_group_name], single=True)

        ip_permissions = [
            {
                "IpProtocol": "tcp",
                "FromPort": 2049,
                "ToPort": 2049,
                "IpRanges": [],
                "Ipv6Ranges": [],
                "PrefixListIds": [],
                "UserIdGroupPairs": [
                    {
                        "GroupId": jenkins_master.id,
                        "UserId": self.environment_api.aws_api.ec2_client.account_id,
                        "Description": "Jenkins Master Service"
                    },
                ]
            }
        ]

        security_group = self.environment_api.provision_security_group(self.configuration.efs_master_security_group_name,
                                                      ip_permissions=ip_permissions,
                                                      description=f"Jenkins EFS security group {self.environment_api.configuration.environment_name}")
        return security_group

    def provision_master_efs_access_point(self, efs_id):
        """
        Provisions an EFS access point.

        :param efs_id: File system ID
        :return:

        """

        efs_access_point = EFSAccessPoint({})
        efs_access_point.region = self.environment_api.region
        efs_access_point.file_system_id = efs_id
        efs_access_point.posix_user = {"Uid": 0, "Gid": 0}
        efs_access_point.root_directory = {
            "Path": "/",
            "CreationInfo": {
                "OwnerUid": 1000,
                "OwnerGid": 1000,
                "Permissions": "755"
            }
        }
        efs_access_point.tags = self.environment_api.configuration.tags
        efs_access_point.tags = [{"Key": "Name", "Value": self.configuration.master_efs_access_point_name}]
        self.environment_api.aws_api.efs_client.provision_access_point(efs_access_point)
        # todo: check if needed.
        self.environment_api.aws_api.efs_client.update_access_point_information(efs_access_point)
        return efs_access_point

    def provision_master_efs_file_system(self):
        """
        Provisions master efs.

        """
        file_system = EFSFileSystem({})
        file_system.region = self.environment_api.region
        file_system.tags = self.environment_api.configuration.tags
        file_system.tags = [{"Key": "Name", "Value": self.configuration.master_file_system_name}]
        file_system.encrypted = True
        self.environment_api.aws_api.efs_client.provision_file_system(file_system)
        return file_system

    def provision_efs_mount_targets(self, efs_id, security_group_id):
        """
        Provisions mount targets for the given EFS file system in all private subnets.
        """

        vpc_private_subnets = self.environment_api.private_subnets
        mount_group = []
        for subnet in vpc_private_subnets:
            mount_target = EFSMountTarget({})
            mount_target.file_system_id = efs_id
            mount_target.subnet_id = subnet.id
            mount_target.security_groups = [security_group_id]
            mount_target.region = self.environment_api.region

            self.environment_api.aws_api.efs_client.provision_mount_target(mount_target)
            logger.info(f"Provisioned mount target in subnet {subnet.id} for file system {efs_id}")
            mount_group.append(mount_target)
        return mount_group

    @property
    def loadbalancer_api(self):
        """
        Init load balancer api

        :return:
        """

        configuration = LoadbalancerAPIConfigurationPolicy()
        configuration.health_check_path = "/login"
        configuration.target_group_protocol = "HTTP"
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
                    "hostPort": 8080,
                    "protocol": "tcp",
                },
            ]

        ecs_api_configuration.task_definition_desired_count = 1
        ecs_api_configuration.launch_type = "FARGATE"
        ecs_api_configuration.kill_old_containers = False

        ecs_api.set_api(loadbalancer_api=self.loadbalancer_api)
        ecs_api.set_api(dns_api=self.dns_api)
        if self.environment_api.git_api is None:
            configuration = GitAPIConfigurationPolicy()
            configuration.remote = "git@github.com:AlexeyBeley/horey.git"
            configuration.ssh_key_file_path = f"/Users/{getpass.getuser()}/.ssh/github_key"
            configuration.git_directory_path = "/opt/git/"
            configuration.branch_name = "main"
            self.environment_api.git_api = GitAPI(configuration)

        ecs_api.prepare_container_build_directory_callback = self.prepare_container_build_directory_callback
        return ecs_api

    def prepare_container_build_directory_callback(self, dir_path: pathlib.Path):
        """

        :param dir_path:
        :return:
        """

        return dir_path / "jenkins_api" / "horey" / "jenkins_api" / "master"
