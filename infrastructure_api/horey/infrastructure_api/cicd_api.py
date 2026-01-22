"""
Standard Load balancing maintainer.

"""
from pathlib import Path
import shutil
import time
import getpass
from typing import List

from horey.aws_api.aws_services_entities.ec2_instance import EC2Instance
from horey.common_utils.storage_service import StorageService
from horey.aws_api.aws_services_entities.s3_bucket import S3Bucket
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
from horey.deployer.remote_deployer import DeploymentTarget, RemoteDeployer
from horey.pip_api.requirement import Requirement
from horey.pip_api.standalone_methods import StandaloneMethods
from horey.aws_api.aws_services_entities.iam_policy import IamPolicy

from horey.h_logger import get_logger
from horey.provision_constructor.provision_constructor import ProvisionConstructor

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
            self.init_clouwatch_api_defaults()
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

    def provision(self):
        """
        Provision CICD infrastructure.

        :return:
        """

        self.provision_master_infrastructure()
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

        # provision_lb_security_groups used for lb_facing_security_group creation.
        self.ecs_api.provision_lb_security_groups()
        # provision_lb_facing_security_group used for efs SG creation.
        self.ecs_api.provision_lb_facing_security_group()
        self.provision_efs()

        self.ecs_api.task_role_inline_policies_callback = self.task_role_inline_policies_callback
        self.ecs_api.provision()

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
                    "Resource":"*"
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

    def prepare_container_build_directory_callback(self, dir_path: Path):
        """

        :param dir_path:
        :return:
        """

        return dir_path / "jenkins_api" / "horey" / "jenkins_api" / "master"

    def generate_deployment_target(self, name=None, target_ssh_key_secret_name=None, bastion=None):
        """
        Generate target

        :param bastion:
        :param target_ssh_key_secret_name:
        :param name:
        :return:
        """

        if name is None:
            raise ValueError("name is None")

        ec2_instance = self.environment_api.get_ec2_instance(tags_dict={"Name": [name]})
        return self.init_deployment_target(ec2_instance, target_ssh_key_secret_name=target_ssh_key_secret_name,
                                                   bastion=bastion)

    def generate_deployment_targets(self, name=None, target_ssh_key_secret_name:str=None, bastion=None) -> List[DeploymentTarget]:
        """
        Generate targets

        :param name:
        :param target_ssh_key_secret_name:
        :param bastion:
        :return:
        """

        if name is None:
            raise ValueError("name is None")

        ec2_instances = self.environment_api.get_ec2_instances(tags_dict={"Name": [name]})
        targets = []
        for ec2_instance in ec2_instances:
            targets.append(self.init_deployment_target(ec2_instance, target_ssh_key_secret_name=target_ssh_key_secret_name, bastion=bastion))
        return targets

    def init_deployment_target(self, ec2_instance: EC2Instance, target_ssh_key_secret_name:str=None, bastion: EC2Instance=None) -> DeploymentTarget:
        """
        Init single target from ec2 Instance

        :param ec2_instance:
        :param target_ssh_key_secret_name:
        :param bastion:
        :return:
        """

        if ec2_instance.get_status() == ec2_instance.State.STOPPED:
            self.environment_api.aws_api.ec2_client.start_instances([ec2_instance])
        target_ssh_key_secret_name = target_ssh_key_secret_name or ec2_instance.key_name
        self.environment_api.aws_api.get_secret_file(target_ssh_key_secret_name,
                                                     self.configuration.deployment_directory,
                                                     region=self.environment_api.region)
        # check the type to be set
        # key_pairs = self.environment_api.aws_api.ec2_client.get_region_key_pairs(self.environment_api.region)

        target = DeploymentTarget()
        target.deployment_target_address = ec2_instance.public_ip_address
        target.deployment_target_user_name = "ubuntu"
        # target.deployment_target_ssh_key_type
        target.deployment_target_ssh_key_path = self.configuration.deployment_directory / target_ssh_key_secret_name

        if bastion:
            target.bastion_address = bastion.public_ip_address
            bastion_ssh_key_secret_name = bastion.key_name
            self.environment_api.aws_api.get_secret_file(bastion_ssh_key_secret_name,
                                                         self.configuration.deployment_directory,
                                                         region=self.environment_api.region)

            target.bastion_ssh_key_path = self.configuration.deployment_directory / bastion_ssh_key_secret_name
            target.bastion_user_name = "ubuntu"

            target.deployment_target_address = ec2_instance.private_ip_address

        return target

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
            self.copy_horey_package_required_packages_to_build_dir("provision_constructor", step.configuration.local_deployment_dir_path, horey_repo_path)
        target.add_step(step)
        return True

    def copy_horey_package_required_packages_to_build_dir(self, package_raw_name: str, build_dir_path: Path, horey_repo_path: Path):
        """
        Copy all needed directories and files.

        :param package_raw_name:
        :param build_dir_path:
        :return:
        """

        base_names = ["pip_api", "build", "Makefile", "pip_api_docker_configuration.py", "pip_api_configuration.py"]

        build_horey_dir_path = build_dir_path / "horey"
        build_horey_dir_path.mkdir()

        requirement = Requirement(None, f"horey.{package_raw_name}")
        venv_dir_path = build_horey_dir_path / "build" / "_build" / "_venv"
        multi_package_repo_to_prefix_map = {"horey.": horey_repo_path}
        requirements_aggregator = {}
        StandaloneMethods(venv_dir_path, multi_package_repo_to_prefix_map).compose_requirements_recursive([requirement],
                                                                                                          requirements_aggregator)
        recursively_found_horey_directories = [requirement_name.split(".")[1] for requirement_name in requirements_aggregator if requirement_name.startswith("horey")]

        def ignore_build(_, file_names):
            return ["_build"] if "_build" in file_names else []

        for obj_name in list(set(base_names + recursively_found_horey_directories)):
            obj_path = horey_repo_path / obj_name
            if obj_path.is_dir():
                shutil.copytree(obj_path, build_horey_dir_path / obj_name, ignore=ignore_build)
            else:
                shutil.copy(obj_path, build_horey_dir_path / obj_name)

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

        ProvisionConstructor.generate_provision_constructor_apply_scripts(target.local_deployment_dir_path, provision_script_generator, target=target)
        raise NotImplementedError("Not implemented")

    def run_remote_provision_constructor(self, target, function_name, **kwargs):
        """
        Run the function remotely

        :return:
        """

        try:
            s3_deployment_uri = kwargs.pop("s3_deployment_uri")
            storage_service = S3StorageService(self.environment_api.aws_api,
                                               s3_deployment_uri) if s3_deployment_uri else None
        except KeyError:
            storage_service = None

        remote_deployer = RemoteDeployer()
        remoter = remote_deployer.get_remoter(target)
        provision_constructor = ProvisionConstructor()
        provision_constructor.deployment_dir = target.local_deployment_dir_path
        return provision_constructor.provision_system_function_remote(remoter, function_name, storage_service=storage_service, **kwargs)


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
        bucket =  S3Bucket({"Name": bucket_name})
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
                                                                custom_filters={"Prefix": self.base_path})]

    def download(self, remote_path: str, local_path: Path):
        """
        Download file from S3.

        :param remote_path:
        :param local_path:
        :return:
        """

        return self.aws_api.s3_client.get_bucket_object_file(self.bucket, S3Bucket.BucketObject({"Key": remote_path}), local_path)
