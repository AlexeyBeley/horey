"""
Standard Load balancing maintainer.

"""
import json
import pathlib
from pathlib import Path
import time
import getpass
from typing import List

from horey.aws_api.aws_services_entities.ec2_instance import EC2Instance
from horey.common_utils.storage_service import StorageService
from horey.aws_api.aws_services_entities.s3_bucket import S3Bucket
from horey.github_api.github_api import GithubAPI
from horey.infrastructure_api.aws_iam_api import AWSIAMAPI, AWSIAMAPIConfigurationPolicy
from horey.infrastructure_api.build_api import BuildAPI, BuildAPIConfigurationPolicy
from horey.infrastructure_api.cloudwatch_api_configuration_policy import CloudwatchAPIConfigurationPolicy
from horey.infrastructure_api.cloudwatch_api import CloudwatchAPI
from horey.infrastructure_api.ec2_api import EC2API, EC2APIConfigurationPolicy
from horey.infrastructure_api.ecs_api import ECSAPI, ECSAPIConfigurationPolicy
from horey.infrastructure_api.cicd_api_configuration_policy import CICDAPIConfigurationPolicy
from horey.infrastructure_api.environment_api import EnvironmentAPI
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI
from horey.infrastructure_api.loadbalancer_api import LoadbalancerAPIConfigurationPolicy
from horey.infrastructure_api.dns_api import DNSAPIConfigurationPolicy
from horey.git_api.git_api import GitAPI, GitAPIConfigurationPolicy
from horey.aws_api.aws_clients.efs_client import EFSFileSystem, EFSAccessPoint, EFSMountTarget
from horey.deployer.remote_deployer import DeploymentTarget, RemoteDeployer
from horey.pip_api.pip_api import StandaloneMethods
from horey.aws_api.aws_services_entities.iam_policy import IamPolicy

from horey.h_logger import get_logger
from horey.provision_constructor.provision_constructor import ProvisionConstructor

logger = get_logger()


class S3StorageService(StorageService):
    """
    Accessing S3 files
    """

    def __init__(self, aws_api, s3_deployment_uri: str):
        """


        :param aws_api:
        :param s3_deployment_uri: s3://bucket_name/base_path
        """

        bucket_name, base_path = s3_deployment_uri.split("s3://")[1].split("/", 1)
        bucket = S3Bucket({"Name": bucket_name})
        self.aws_api = aws_api
        self.bucket = bucket
        self.base_path = base_path


    def upload(self, local_path: Path, remote_path: str):
        """
        Upload file to S3.

        :param local_path:
        :param remote_path:
        :return:
        """

        raise NotImplementedError(f"{local_path=}, {remote_path=}")

    def list(self) -> List[str]:
        """
        List all files in the bucket.

        :return:
        """

        return [obj.key for obj in self.aws_api.s3_client.yield_bucket_objects(None,
                                                                               bucket_name=self.bucket.name,
                                                                               custom_filters={
                                                                                   "Prefix": self.base_path})]

    def download(self, remote_path: str, local_path: Path):
        """
        Download file from S3.

        :param remote_path:
        :param local_path:
        :return:
        """

        return self.aws_api.s3_client.get_bucket_object_file(self.bucket, S3Bucket.BucketObject({"Key": remote_path}),
                                                             local_path)


class CICDAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration: CICDAPIConfigurationPolicy, environment_api: EnvironmentAPI):
        self.configuration = configuration
        self.environment_api = environment_api
        self._cloudwatch_api = None
        self._jenkins_master_ecs_api = None
        self._ec2_api = None
        self._dns_api = None
        self._remote_deployer = None
        self._iam_api = None
        self._build_api = None
    
    @property
    def remote_deployer(self):
        """
        Remote deployer

        :return:
        """

        if self._remote_deployer is None:
            self._remote_deployer = RemoteDeployer()
        return self._remote_deployer

    @property
    def cloudwatch_api(self):
        """
        Standard.

        :return:
        """

        if self._cloudwatch_api is None:
            config = CloudwatchAPIConfigurationPolicy()
            self._cloudwatch_api = CloudwatchAPI(configuration=config, environment_api=self.environment_api)
            self.init_clouwatch_api_defaults()
        return self._cloudwatch_api

    @property
    def hagent_build_api(self):
        """
        Standard.

        :return:
        """

        if self._build_api is None:
            config = BuildAPIConfigurationPolicy()
            self._build_api = BuildAPI(configuration=config, environment_api=self.environment_api)
            self._build_api.git_api = self._build_api.horey_git_api
        return self._build_api

    @property
    def ec2_api(self):
        """
        Standard.

        :return:
        """

        if self._ec2_api is None:
            config = EC2APIConfigurationPolicy()
            self._ec2_api = EC2API(configuration=config, environment_api=self.environment_api)
        return self._ec2_api

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
            self.ecs_api.set_api(cloudwatch_api=self.cloudwatch_api)
            self.init_clouwatch_api_defaults()

        if dns_api:
            self._dns_api = dns_api

    def init_clouwatch_api_defaults(self):
        """
        Init default configs

        :return:
        """

        try:
            self.cloudwatch_api.configuration.log_group_name
        except self._cloudwatch_api.configuration.UndefinedValueError:
            self.cloudwatch_api.configuration.log_group_name = self.ecs_api.configuration.cloudwatch_log_group_name

    def provision_jenkins_master(self):
        """
        Provision CICD infrastructure.

        :return:
        """
        self.provision_jenkins_master_infrastructure()
        self.update_jenkins_master()
        self.jenkins_master_ecs_api.provision_ecs_task_definition(self.ecs_api.ecr_repo_uri + ":latest")
        self.cloudwatch_api.provision()

    def update_jenkins_master(self, branch_name=None):
        """
        Jenkins Master update.

        :return:
        """

        build_number = self.jenkins_master_ecs_api.get_next_build_number()
        image = self.jenkins_master_ecs_api.build_api.run_build_and_upload_image_routine(branch_name, build_number)

        image_registry_reference = image.tags[0]
        td = self.jenkins_master_ecs_api.generate_ecs_task_definition(image_registry_reference,
                                                       slug="jenkins-master", requires_compatibilities=["FARGATE"])
        (_,
         jenkins_master_access_point_name,
         jenkins_master_efs_file_system_name) = self.generate_jenkins_master_efs_component_names()

        master_efs = self.get_efs_file_system(jenkins_master_efs_file_system_name)
        access_point = self.get_efs_access_point(master_efs.id, jenkins_master_access_point_name)
        volumes, mount_points = self.generate_jenkins_master_volume_and_mount_configuration(master_efs, access_point,
                                                                             "/var/jenkins_home")

        td.set_storage(volumes=volumes, mount_points=mount_points)

        task_role = self.iam_api.get_role(self.get_task_role_name("jenkins-master")
                                                )

        exec_role = self.iam_api.get_role(self.get_task_role_name("jenkins-master-exec"))

        td.set_roles(task_role=task_role.arn, execution_role=exec_role.arn)
        td.set_ports(container_port=8080, host_port=8080)

        self.jenkins_master_ecs_api.provision_ecs_task_definition_ng(td)
        target_group = self.loadbalancer_api.get_targetgroup(name=f"tg-cluster-{self.environment_api.configuration.project_name_abbr}-{self.environment_api.configuration.environment_level_abbr}-mgmt-jenkins")
        breakpoint()
        self.jenkins_master_ecs_api.provision_ecs_service(td, target_groups=[target_group])
        breakpoint()

    def get_efs_file_system(self, file_system_name):
        """
        Get EFS file system.

        :return:
        """
        file_system = EFSFileSystem({})
        file_system.region = self.environment_api.region
        file_system.tags = self.environment_api.configuration.tags
        file_system.tags = [{"Key": "Name", "Value": file_system_name}]
        file_system.encrypted = True
        if not self.environment_api.aws_api.efs_client.update_file_system_information(file_system):
            raise ValueError("EFS file system was not found")

        return file_system

    def get_efs_access_point(self, file_system_id, access_point_name):
        """
        Get EFS access point.

        :return:
        """

        efs_access_point = EFSAccessPoint({})
        efs_access_point.region = self.environment_api.region
        efs_access_point.file_system_id = file_system_id
        efs_access_point.tags = self.environment_api.configuration.tags
        efs_access_point.tags = [{"Key": "Name", "Value": access_point_name}]
        if not self.environment_api.aws_api.efs_client.update_access_point_information(efs_access_point):
            raise ValueError("EFS access point was not found")

        return efs_access_point

    def provision_jenkins_master_infrastructure(self):
        """
        Jenkins Master infra

        :return:
        """
        self.jenkins_master_ecs_api.provision_service_log_group()
        master_service_security_group = self.ec2_api.provision_security_group(f"sg_{self.environment_api.configuration.environment_level}-jenkins-master-service")
        load_balancer_security_group = self.ec2_api.provision_internal_alb_security_group()
        self.ec2_api.security_group_add_rule(master_service_security_group, source_group=load_balancer_security_group, port_range=(8080, 8080))
        jenkins_master_efs_security_group_name, jenkins_master_access_point_name, jenkins_master_efs_file_system_name = self.generate_jenkins_master_efs_component_names()

        # todo: uncomment when ready
        # self.provision_efs(jenkins_master_efs_security_group_name,
        #                   jenkins_master_access_point_name,
        #                   jenkins_master_efs_file_system_name)
        # self.ec2_api.security_group_add_rule(self.ec2_api.get_security_group(jenkins_master_efs_security_group_name), source_group=master_service_security_group, port_range=(2049, 2049))
        assume_role_policy_document = json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ecs-tasks.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        })

        task_role = self.iam_api.provision_role(role_name=self.get_task_role_name("jenkins-master"),
                                                assume_role_policy=assume_role_policy_document)

        exec_role = self.jenkins_master_ecs_api.provision_execution_role(name=self.get_task_role_name("jenkins-master-exec"),
                                                )


        policy_text = self.iam_api.generate_ecr_repository_policy(ecs_task_execution_role=exec_role)

        self.jenkins_master_ecs_api.provision_ecr_repository(repository_policy=policy_text)
        breakpoint()
        cluster_name = (f"{self.environment_api.configuration.project_name_abbr}-"
                f"{self.environment_api.configuration.environment_level}-"
                f"management")

        cluster = self.jenkins_master_ecs_api.provision_cluster(cluster_name=cluster_name)
        self.jenkins_master_ecs_api.provision_ecs_autoscaling_group_capacity_provider(cluster, "management")
        return True

    def generate_jenkins_master_efs_component_names(self):
        """
        Generate Jenkins master EFS names:
                jenkins_master_efs_security_group_name
                jenkins_master_access_point_name
                jenkins_master_efs_file_system_name

        :return:
        """

        return (f"sg_{self.environment_api.configuration.environment_level}" \
                                         f"-jenkins-master",
               f"acp_{self.environment_api.configuration.environment_level}" \
                                       f"-management-jenkins",
               f"fs_{self.environment_api.configuration.environment_level}" \
                                      f"-management-jenkins")

    def get_task_role_name(self, slug):
        """
        Generate task role name.

        :param slug:
        :return:
        """

        return f"role_{self.environment_api.configuration.environment_level}_{slug}"

    def task_role_inline_policies_callback(self):
        """
        Generate inline policies.

        :return:
        """

        return [self.generate_ssm_task_role_inline_policy(), self.generate_ec2_task_role_inline_policy()]

    def generate_ssm_task_role_inline_policy(self):
        """
        Trivial

        :return:
        """

        policy_ssm = IamPolicy({})
        policy_ssm.document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "ssmmessages:CreateControlChannel",
                        "ssmmessages:CreateDataChannel",
                        "ssmmessages:OpenControlChannel",
                        "ssmmessages:OpenDataChannel"
                    ],
                    "Resource": "*",
                    "Condition": {
                        "StringEquals": {
                            "aws:ResourceTag/env_level": self.environment_api.configuration.environment_level,
                            "aws:PrincipalTag/env_level": self.environment_api.configuration.environment_level,
                            "aws:ResourceTag/env_name": self.environment_api.configuration.environment_name,
                            "aws:PrincipalTag/env_name": self.environment_api.configuration.environment_name,
                            "aws:ResourceTag/project_name": self.environment_api.configuration.project_name,
                            "aws:PrincipalTag/project_name": self.environment_api.configuration.project_name,
                        }
                    }
                }
            ]
        }
        policy_ssm.name = "inline_ssm_messages"
        policy_ssm.description = "Allow task to access SSM service for remote connections"
        policy_ssm.tags = self.environment_api.configuration.tags
        policy_ssm.tags.append({
            "Key": "Name",
            "Value": policy_ssm.name
        })
        return policy_ssm

    def generate_ec2_task_role_inline_policy(self):
        """
        Trivial
                    "Condition": {
                        "StringEquals": {
                            "aws:ResourceTag/env_level": self.environment_api.configuration.environment_level,
                            "aws:PrincipalTag/env_level": self.environment_api.configuration.environment_level,
                            "aws:ResourceTag/env_name": self.environment_api.configuration.environment_name,
                            "aws:PrincipalTag/env_name": self.environment_api.configuration.environment_name,
                            "aws:ResourceTag/project_name": self.environment_api.configuration.project_name,
                            "aws:PrincipalTag/project_name": self.environment_api.configuration.project_name,
                        }
                    }

        :return:
        """

        policy_ec2 = IamPolicy({})
        policy_ec2.document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "ec2:DescribeSpotFleetInstances",
                        "ec2:ModifySpotFleetRequest",
                        "ec2:CreateTags",
                        "ec2:DescribeRegions",
                        "ec2:DescribeInstances",
                        "ec2:TerminateInstances",
                        "ec2:DescribeInstanceStatus",
                        "ec2:DescribeSpotFleetRequests",
                        "ec2:DescribeFleets",
                        "ec2:DescribeFleetInstances",
                        "ec2:ModifyFleet",
                        "ec2:DescribeInstanceTypes"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "autoscaling:DescribeAutoScalingGroups",
                        "autoscaling:TerminateInstanceInAutoScalingGroup",
                        "autoscaling:UpdateAutoScalingGroup"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "iam:ListInstanceProfiles",
                        "iam:ListRoles"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "iam:PassRole"
                    ],
                    "Resource": "*"
                }
            ]
        }
        policy_ec2.name = "inline_ec2"
        policy_ec2.description = "Allow Jenkins master to control EC2 autoscaling"
        policy_ec2.tags = self.environment_api.configuration.tags
        policy_ec2.tags.append({
            "Key": "Name",
            "Value": policy_ec2.name
        })

        return policy_ec2

    def update(self):
        """
        aws ecs execute-command --region us-east-1 --cluster cluster-name --task 97e87487c0a74421ab53c2fed0a726cc  --container container-name --command "/bin/sh" --interactive
        :return:
        """
        perf_counter_start = time.perf_counter()
        overrides = {"containerOverrides": [{"name": self.ecs_api.configuration.container_name,
                                             "environment": [{"name": key, "value": value} for key, value in
                                                             self.configuration.build_environment_variable.items()]}]}

        task = self.ecs_api.start_task(overrides=overrides)
        response = self.ecs_api.wait_for_task_to_finish(task)
        logger.info(f"Time took from triggering task to its completion: {time.perf_counter() - perf_counter_start}")
        return response

    def provision_efs(self, security_group_name,
                           access_point_name,
                           file_system_name):
        """
        Standard.
        --volume jenkins-data:/var/jenkins_home

        :return:
        """

        efs_security_group = self.ec2_api.provision_security_group(name=security_group_name)
        master_efs = self.provision_master_efs_file_system(file_system_name)
        access_point = self.provision_master_efs_access_point(master_efs.id, access_point_name)
        self.provision_efs_mount_targets(master_efs.id, efs_security_group.id)
        volume, mount_point = self.generate_jenkins_master_volume_and_mount_configuration(master_efs, access_point,
                                                                             "/var/jenkins_home")
        return volume, mount_point

    @staticmethod
    def generate_jenkins_master_volume_and_mount_configuration(efs, access_point, container_path):
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

    def provision_master_efs_access_point(self, efs_id, access_point_name):
        """
        Provisions an EFS access point.

        :param efs_id: File system ID
        :return:

        """

        efs_access_point = EFSAccessPoint({})
        efs_access_point.region = self.environment_api.region
        efs_access_point.file_system_id = efs_id
        efs_access_point.posix_user = {"Uid": 1000, "Gid": 1000}
        efs_access_point.root_directory = {
            "Path": "/",
            "CreationInfo": {
                "OwnerUid": 1000,
                "OwnerGid": 1000,
                "Permissions": "755"
            }
        }
        efs_access_point.tags = self.environment_api.configuration.tags
        efs_access_point.tags = [{"Key": "Name", "Value": access_point_name}]
        self.environment_api.aws_api.efs_client.provision_access_point(efs_access_point)
        return efs_access_point

    def provision_master_efs_file_system(self, file_system_name):
        """
        Provisions master efs.

        """
        file_system = EFSFileSystem({})
        file_system.region = self.environment_api.region
        file_system.tags = self.environment_api.configuration.tags
        file_system.tags = [{"Key": "Name", "Value": file_system_name}]
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

    @property
    def iam_api(self):
        """
        Generate environment config

        :return:
        """

        if self._iam_api is None:

            self._iam_api = AWSIAMAPI(AWSIAMAPIConfigurationPolicy(), self.environment_api)

        return self._iam_api

    @property
    def jenkins_master_ecs_api(self):
        """
        Generate environment config

        :return:
        """
        if self._jenkins_master_ecs_api is None:
            ecs_api_configuration = ECSAPIConfigurationPolicy()
            ecs_api_configuration.service_name = "jenkins"
            ecs_api = ECSAPI(ecs_api_configuration, self.environment_api)

            ecs_api_configuration.ecs_task_definition_cpu_reservation = 1024
            ecs_api_configuration.ecs_task_definition_memory_reservation = 2048
            ecs_api_configuration.autoscaling_max_capacity = 1
            ecs_api_configuration.network_mode = "awsvpc"
            ecs_api_configuration.cluster_name = f"cluster-{self.environment_api.configuration.project_name_abbr}-{self.environment_api.configuration.environment_level}-{self.environment_api.configuration.environment_name}"

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
            ecs_api_configuration.security_groups = [f"sg_{self.environment_api.configuration.project_name_abbr}-{self.environment_api.configuration.environment_level}-{self.environment_api.configuration.environment_name}-jenkins"]
            ecs_api.build_api.prepare_docker_image_build_directory_callback = self.prepare_jenkins_master_container_build_directory_callback

            ecs_api.build_api.configuration.docker_repository_uri = f"{self.environment_api.aws_api.ecs_client.account_id}.dkr.ecr.{ecs_api.configuration.ecr_repository_region}.amazonaws.com/{ecs_api_configuration.ecr_repository_name}"

            ecs_api.set_ecr_repository_name(f"repo_{self.environment_api.configuration.environment_level}_jenkins_master")

            self._jenkins_master_ecs_api = ecs_api
        return self._jenkins_master_ecs_api

    @property
    def jenkins_hagent_ecs_api(self):
        """
        Generate environment config

        :return:
        """
        if self._ecs_api is None:
            ecs_api_configuration = ECSAPIConfigurationPolicy()
            ecs_api_configuration.slug = "hagent"
            ecs_api = ECSAPI(ecs_api_configuration, self.environment_api)

            ecs_api_configuration.ecs_task_definition_cpu_reservation = 1024
            ecs_api_configuration.ecs_task_definition_memory_reservation = 2048
            ecs_api_configuration.autoscaling_max_capacity = 1
            ecs_api_configuration.network_mode = "awsvpc"

            ecs_api_configuration.task_definition_desired_count = 1
            ecs_api_configuration.launch_type = "EC2"
            ecs_api_configuration.kill_old_containers = False

            if self.environment_api.git_api is None:
                configuration = GitAPIConfigurationPolicy()
                configuration.remote = "git@github.com:AlexeyBeley/horey.git"
                configuration.ssh_key_file_path = f"/Users/{getpass.getuser()}/.ssh/github_key"
                configuration.git_directory_path = "/opt/git/"
                configuration.branch_name = "main"
                self.environment_api.git_api = GitAPI(configuration)

            ecs_api.prepare_container_build_directory_callback = self.prepare_container_build_directory_callback
            self._ecs_api = ecs_api
        return self._ecs_api

    def prepare_jenkins_master_container_build_directory_callback(self, dir_path: Path):
        """

        :param dir_path:
        :return:
        """

        return dir_path / "jenkins_api" / "horey" / "jenkins_api" / "master"

    def generate_deployment_target(self, name=None, target_ssh_key_secret_name=None, bastions=None):
        """
        Generate target

        :param bastions:
        :param target_ssh_key_secret_name:
        :param name:
        :return:
        """

        if name is None:
            raise ValueError("name is None")

        ec2_instance = self.environment_api.get_ec2_instance(tags_dict={"Name": [name]})
        return self.init_deployment_target(ec2_instance, target_ssh_key_secret_name=target_ssh_key_secret_name,
                                           bastions=bastions)

    def generate_deployment_targets(self, name=None, target_ssh_key_secret_name: str = None, bastions=None) -> List[
        DeploymentTarget]:
        """
        Generate targets

        :param name:
        :param target_ssh_key_secret_name:
        :param bastions:
        :return:
        """

        if name is None:
            raise ValueError("name is None")

        ec2_instances = self.environment_api.get_ec2_instances(tags_dict={"Name": [name]})
        targets = []
        for ec2_instance in ec2_instances:
            targets.append(
                self.init_deployment_target(ec2_instance, target_ssh_key_secret_name=target_ssh_key_secret_name,
                                            bastions=bastions))
        return targets

    def init_deployment_target(self, ec2_instance: EC2Instance, target_ssh_key_secret_name: str = None,
                               bastions: List[EC2Instance] = None) -> DeploymentTarget:
        """
        Init single target from ec2 Instance

        :param ec2_instance:
        :param target_ssh_key_secret_name:
        :param bastions:
        :return:
        """

        bastions = bastions or []

        if ec2_instance.get_status() == ec2_instance.State.STOPPED:
            self.environment_api.aws_api.ec2_client.start_instances([ec2_instance])
        target_ssh_key_secret_name = target_ssh_key_secret_name or ec2_instance.key_name
        self.environment_api.aws_api.get_secret_file(target_ssh_key_secret_name,
                                                     self.configuration.deployment_directory,
                                                     region=self.environment_api.region)
        # check the type to be set
        # key_pairs = self.environment_api.aws_api.ec2_client.get_region_key_pairs(self.environment_api.region)

        target = DeploymentTarget()
        target.deployment_target_user_name = "ubuntu"
        # target.deployment_target_ssh_key_type
        target.deployment_target_ssh_key_path = self.configuration.deployment_directory / target_ssh_key_secret_name
        target.deployment_target_address = ec2_instance.private_ip_address
        if bastions:
            chain_link = self.init_bastion_chain_link(bastions[0], bastions[0].public_ip_address)
            target.bastion_chain.append(chain_link)

        for bastion in bastions[1:]:
            chain_link = self.init_bastion_chain_link(bastion, bastion.private_ip_address)
            target.bastion_chain.append(chain_link)

        return target

    def init_bastion_chain_link(self, ec2_instance: EC2Instance, address: str, ) -> DeploymentTarget.BastionChainLink:
        """

        :param address:
        :param address:
        :param ec2_instance:
        :return:
        """

        self.environment_api.aws_api.get_secret_file(ec2_instance.key_name,
                                                     self.configuration.deployment_directory,
                                                     region=self.environment_api.region)

        bastion_ssh_key_path = self.configuration.deployment_directory / ec2_instance.key_name
        return DeploymentTarget.BastionChainLink(address, bastion_ssh_key_path)

    @staticmethod
    def init_bastion_chain_link_raw(address, key_file_path, user_name="ubuntu"):
        """
        From raw params

        :param user_name:
        :param address:
        :param key_file_path:
        :return:
        """

        return DeploymentTarget.BastionChainLink(address, key_file_path, user_name=user_name)

    def add_install_provision_constructor_step(self, target: DeploymentTarget, horey_repo_path=None):
        """
        Install the provision_constructor

        :param horey_repo_path:
        :param target:
        :return:
        """

        ProvisionConstructor.generate_provision_constructor_bootstrap_script(target.local_deployment_dir_path,
                                                                             "provision_constructor_install.sh")

        step = target.generate_step("provision_constructor_install.sh")
        (step.configuration.local_deployment_dir_path / step.configuration.data_dir_name).mkdir(exist_ok=True,
                                                                                                parents=True)
        step.configuration.generate_configuration_file_ng(step.configuration.local_deployment_dir_path /
                                                          step.configuration.data_dir_name /
                                                          step.configuration.script_configuration_file_name)
        if horey_repo_path:
            StandaloneMethods.copy_horey_package_required_packages_to_build_dir("provision_constructor",
                                                                                step.configuration.local_deployment_dir_path,
                                                                                horey_repo_path)
        target.add_step(step)
        return True

    def add_provision_constructor_system_function(self, dst_file_path: Path, system_function_name: str, **kwargs):
        """
        Add function to the provisioner script.

        :param dst_file_path:
        :param system_function_name:
        :param kwargs:
        :return:
        """

        ProvisionConstructor().add_system_function_trigger_to_step_script(system_function_name, dst_file_path, **kwargs)

    def add_step_provision_constructor_apply(self, target, provision_script_generator):
        """
        Generate and add the step.

        :param target:
        :param provision_script_generator:
        :return:
        """

        ProvisionConstructor.generate_provision_constructor_apply_scripts(target.local_deployment_dir_path,
                                                                          provision_script_generator, target=target)
        raise NotImplementedError("Not implemented")

    def run_remote_provision_constructor(self, target, function_name, windows=False, timeout=60*60, **kwargs):
        """
        Run the function remotely

        :return:
        """

        if target.status_code in [target.StatusCode.FAILURE, target.StatusCode.ERROR]:
            raise self.remote_deployer.DeployerError(f"Target deployment stopped: {target.deployment_target_address}")

        logger.info(f"run_remote_provision_constructor {timeout=}, {windows=}")
        try:
            s3_deployment_uri = kwargs.pop("s3_deployment_uri")
            storage_service = S3StorageService(self.environment_api.aws_api,
                                               s3_deployment_uri) if s3_deployment_uri else None
        except KeyError:
            storage_service = None

        remoter = self.remote_deployer.get_remoter(target, windows=windows, default_timeout=timeout)
        provision_constructor = ProvisionConstructor()
        provision_constructor.deployment_dir = target.local_deployment_dir_path
        return provision_constructor.provision_system_function_remote(remoter, function_name,
                                                                      storage_service=storage_service, **kwargs)

    def run_remote_deployer_deploy_targets(self, targets, asynchronous=True):
        """
        Run the deployment

        :param asynchronous:
        :param targets:
        :return:
        """

        return self.remote_deployer.deploy_targets(targets, asynchronous=asynchronous)

    def provision_jenkins_hagent_infrastructure(self):
        """
        Jenkins hagent infra

        :return:
        """
        assume_role_policy_document = json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ecs-tasks.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        })

        task_role = self.iam_api.provision_role(role_name=self.get_task_role_name("jenkins-hagent"),
                                                assume_role_policy=assume_role_policy_document)

        exec_role = self.iam_api.provision_role(role_name=self.get_task_role_name("jenkins-hagent-exec"),
                                                assume_role_policy=assume_role_policy_document)
        policy_text = self.iam_api.generate_ecr_repository_policy(ecs_task_execution_role=exec_role)

        self.ecs_api.provision_ecr_repository(repository_name = self.generate_hagent_repository_name(), repository_policy=policy_text)

        cluster_name = self.generate_management_cluster_name()
        self.ecs_api.provision_service_log_group(cluster_name, "hagent")
        self.update_hagent()
        return True

    def generate_management_cluster_name(self):
        """
        Generate name

        :return:
        """

        return (f"{self.environment_api.configuration.project_name_abbr}-"
                f"{self.environment_api.configuration.environment_level}-"
                f"management")

    def generate_hagent_repository_name(self):
        """
        Generate name
        :return:
        """
        return f"repo_{self.environment_api.configuration.environment_level}_jenkins_hagent"

    def update_hagent(self, branch_name=None, from_docker_repository=False):
        """
        Update jenkins hagent

        :param branch_name:
        :param from_docker_repository:
        :return:
        """

        self.hagent_ecs_api.configuration.slug = "hagent"

        self.ecs_api.build_api.prepare_docker_image_build_directory = self.prepare_hagent_container_build_directory
        if from_docker_repository:
            image_tag_raw = self.ecs_api.fetch_latest_artifact_metadata().image_tags[0]
            image_registry_reference = self.ecs_api.generate_image_registry_reference(image_tag_raw)
        else:
            build_number = self.ecs_api.get_next_build_number()

            self.ecs_api.build_api.configuration.docker_build_arguments["platform"] = "linux/amd64"
            self.ecs_api.build_api.configuration.docker_build_arguments["pull"] = True

            repo_name = self.generate_hagent_repository_name()
            self.ecs_api.build_api.configuration.docker_repository_uri = f"{self.environment_api.aws_api.ecs_client.account_id}.dkr.ecr.{self.ecs_api.configuration.ecr_repository_region}.amazonaws.com/{repo_name}"

            image = self.ecs_api.build_api.run_build_and_upload_image_routine(branch_name, build_number)

            image_registry_reference = image.tags[0]

        td = self.ecs_api.generate_ecs_task_definition(image_registry_reference, cluster_name=self.generate_management_cluster_name(), slug="hagent", requires_compatibilities=["EC2"])
        linux_params = {"devices" :[{
            'hostPath': '/var/run/docker.sock',
            'containerPath': '/var/run/docker.sock',
            'permissions': [
                'write',
            ]
        },
        ]}
        raise NotImplementedError("Not implemented")
        # self.jenkins_hagent_ecs_api.generate_ecs_task_definition_storage(td, linux_params=linux_params)


        # self.jenkins_hagent_ecs_api.provision_ecs_task_definition_ng(td)

    def prepare_hagent_container_build_directory(self, dir_path: pathlib.Path, build_number):
        """
        Callback to prepare the build directory for the hagent.

        :param build_number:
        :param dir_path:
        :return:
        """

        build_dir_path = self.ecs_api.build_api.prepare_docker_image_horey_package_build_directory(dir_path, "docker_api", build_number)
        entrypoint_name = "docker_builder.py"
        with open(build_dir_path / entrypoint_name, "w", encoding="utf-8") as fh:
            fh.writelines([
                "from horey.docker_api.docker_api import DockerAPI\n",
                "docker_api = DockerAPI()\n",
                "print(docker_api.get_all_images())\n"
                ])
        self.ecs_api.build_api.add_docker_instruction_copy(build_dir_path, entrypoint_name)
        self.ecs_api.build_api.add_docker_instruction_entrypoint(build_dir_path, f'["python", "{entrypoint_name}"]')


        # docker run --mount type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock -it --entrypoint=/bin/bash test

        return build_dir_path


    def provision_github_hagent(self, github_api: GithubAPI, bastions: List[EC2Instance] = None, repository_name=None):
        """
        Provision jenkins triggering github runner

        :return:
        """

        github_token = github_api.request_repository_runner_registration_token(repository_name)

        sec_group = self.ec2_api.provision_security_group(name = self.configuration.github_hagent_security_group_name, description=f"{self.environment_api.configuration.environment_name}, {self.environment_api.configuration.environment_level}")
        if bastions:
            self.ec2_api.security_group_add_rule(sec_group, source_group=bastions[-1].security_groups[0]["GroupId"], port_range=[22,22])

        ec2_instance = self.ec2_api.provision_ubuntu_24_04_instance(
            name=f"{self.environment_api.configuration.environment_level}-github-runner",
            security_groups=[sec_group],
            volume_size=30,
            instance_type="t3a.small",
            asynchronous=False)

        target = self.init_deployment_target(ec2_instance, bastions=bastions)

        def entrypoint():
            self.run_remote_provision_constructor(target,
                                                  "github_agent",
                                                  github_token=github_token["token"],
                                                  repo_name= repository_name,
                                                  repo_owner=github_api.configuration.owner
                                                  )

        target.append_remote_step("ProvisionGithub", entrypoint)
        assert self.run_remote_deployer_deploy_targets([target], asynchronous=False)

    def prepare_github_hagent_docker_build_dir(self, _src_dir, build_number) -> Path:
        """
        Create tmp build dir

        :param _src_dir:
        :param build_id:
        :return:
        """

        self.hagent_build_api.prepare_docker_image_horey_package_build_directory(_src_dir, "jenkins_api", build_number)
        return self.hagent_build_api.docker_build_directory

    def provision_github_hagent_dockerized(self, github_api: GithubAPI, bastions: List[EC2Instance] = None, repository_name=None, horey_repo_path=None):
        """
        Provision multirunner.

        :return:
        """

        branch_name = None
        build_number = 1
        self.hagent_build_api.git_api.configuration.directory_path = horey_repo_path
        self.hagent_build_api.docker_build_directory = Path("/tmp") / f"github_hagent_{build_number}"
        github_api.init_hagent_docker_build_dir(self.hagent_build_api.docker_build_directory)
        self.hagent_build_api.prepare_source_code_directory = lambda _build_number: horey_repo_path
        self.hagent_build_api.prepare_docker_image_build_directory = self.prepare_github_hagent_docker_build_dir

        # todo: uncomment:
        # image = self.hagent_build_api.run_prepare_and_build_image_routine(branch_name, build_number, tags=["github_hagent"])
        # todo: remove:
        # image = self.environment_api.docker_api.get_image("github_hagent:latest")
        ret = self.environment_api.docker_api.get_all_images()
        for image in ret:
            if not image.tags:
                continue
            if image.tags[0] == "github_hagent:latest":
                break
        else:
            raise NotImplementedError("Not implemented")


        image_file_path = Path("/tmp/github_hagent_image.tar")
        self.environment_api.docker_api.save(image, image_file_path)

        ec2_instance = self.provision_github_hagent_ec2_instance(bastions=bastions)

        github_token = github_api.delete_repository_runner(repository_name, repository_name)
        github_token = github_api.request_repository_runner_registration_token(repository_name)
        def entrypoint():
            self.run_remote_provision_constructor(target,
                                                  "docker",
                                                  )
            self.run_remote_provision_constructor(target,
                                                  "docker",
                                                  action="copy_image_file",
                                                  image_file=image_file_path,
                                                  tag="github_hagent:latest"
                                                  )

            self.run_remote_provision_constructor(target,
                                                  "github_agent",
                                                  action="start_container",
                                                  image_name="github_hagent:latest",
                                                  github_token=github_token["token"],
                                                  repo_name=repository_name,
                                                  repo_owner=github_api.configuration.owner
                                                  )

        target = self.init_deployment_target(ec2_instance, bastions=bastions)
        target.append_remote_step("ProvisionGithub", entrypoint)
        assert self.run_remote_deployer_deploy_targets([target], asynchronous=False)


    def provision_github_hagent_ec2_instance(self, bastions=None):
        """
        Provision an instance.

        :param bastions:
        :return:
        """

        sec_group = self.ec2_api.provision_security_group(name = self.configuration.github_hagent_security_group_name, description=f"{self.environment_api.configuration.environment_name}, {self.environment_api.configuration.environment_level}")
        if bastions:
            self.ec2_api.security_group_add_rule(sec_group, source_group=bastions[-1].security_groups[0]["GroupId"], port_range=[22,22])

        ec2_instance = self.ec2_api.provision_ubuntu_24_04_instance(
            name=f"{self.environment_api.configuration.environment_level}-github-runner",
            security_groups=[sec_group],
            volume_size=30,
            instance_type="t3a.small",
            asynchronous=False)
        return ec2_instance
