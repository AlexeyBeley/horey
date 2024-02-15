"""
Async orchestrator

"""
import copy
import datetime
import json
import os
import shutil

from horey.h_logger import get_logger
from horey.docker_api.docker_api import DockerAPI
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.aws_api.aws_services_entities.vpc import VPC
from horey.aws_api.aws_services_entities.subnet import Subnet
from horey.aws_api.aws_services_entities.ecr_repository import ECRRepository
from horey.aws_api.base_entities.region import Region
from horey.network.ip import IP

from horey.aws_api.aws_services_entities.rds_db_cluster import RDSDBCluster
from horey.aws_api.aws_services_entities.rds_db_instance import RDSDBInstance
from horey.aws_api.aws_services_entities.rds_db_parameter_group import RDSDBParameterGroup
from horey.aws_api.aws_services_entities.ec2_security_group import EC2SecurityGroup
from horey.aws_api.aws_services_entities.rds_db_cluster_parameter_group import RDSDBClusterParameterGroup
from horey.aws_api.aws_services_entities.rds_db_subnet_group import RDSDBSubnetGroup
from horey.aws_api.aws_services_entities.ecs_cluster import ECSCluster
from horey.aws_api.aws_services_entities.ecs_task_definition import ECSTaskDefinition
from horey.aws_api.aws_services_entities.iam_role import IamRole


logger = get_logger()


class LionKing:
    """
    Main class.

    """

    def __init__(self, configuration):
        self.configuration = configuration
        self._aws_api = None
        self._docker_api = None
        self._region = None
        self._vpc = None
        self._subnets = None
        self.tags = [{"Key": "environment_name",
                      "Value": self.configuration.environment_name},
                      {"Key": "environment_level",
                       "Value": self.configuration.environment_level},
                      {"Key": "project_name",
                       "Value": self.configuration.project_name},
                      ]

    @property
    def aws_api(self):
        """
        AWS API used for the deployment.

        :return:
        """
        if self._aws_api is None:
            aws_api_configuration = AWSAPIConfigurationPolicy()
            aws_api_configuration.configuration_file_full_path = self.configuration.aws_api_configuration_file_full_path
            aws_api_configuration.init_from_file()
            self._aws_api = AWSAPI(aws_api_configuration)

        return self._aws_api

    @property
    def docker_api(self):
        """
        AWS API used for the deployment.

        :return:
        """
        if self._docker_api is None:
            self._docker_api = DockerAPI()

        return self._docker_api

    @property
    def region(self):
        """
        Deployment region.

        :return:
        """

        if self._region is None:
            self._region = Region.get_region(self.configuration.region)

        return self._region

    @property
    def aws_account(self):
        """
        AWS account id.

        :return:
        """

        return self.aws_api.sts_client.get_account()

    @property
    def vpc(self):
        """
        Init vpc

        :return:
        """

        if self._vpc is None:
            filters = [{
                "Name": "tag:environment_name",
                "Values": [
                    self.configuration.environment_name
                ]
            }]

            vpcs = self.aws_api.ec2_client.get_region_vpcs(self.region, filters=filters)
            for vpc in vpcs:
                if vpc.get_tag("project_name") == self.configuration.project_name:
                    break
            else:
                raise RuntimeError(f"Can not find VPC '{self.configuration.environment_name=}' "
                                   f"'{self.configuration.project_name=}'")
            self._vpc = vpc

        return self._vpc

    @property
    def subnets(self):
        """
        Init subnets

        :return:
        """

        if self._subnets is None:

            all_subnets = self.aws_api.ec2_client.get_region_subnets(region=self.region)

            subnets = [subnet for subnet in all_subnets if \
                       subnet.get_tag("environment_name", ignore_missing_tag=True) == self.configuration.environment_name and \
                       subnet.get_tag("project_name", ignore_missing_tag=True) == self.configuration.project_name]

            if len(subnets) != self.configuration.availability_zones_count*2:
                raise RuntimeError(f"Disposing subnets: expected:{self.configuration.availability_zones_count*2:}, found: {len(subnets)}")

            self._subnets = subnets

        return self._subnets

    def provision_vpc(self):
        """
        Provision VPC.

        :return:
        """

        vpc = VPC({})
        vpc.region = self.region
        vpc.cidr_block = self.configuration.vpc_cidr_block

        vpc.tags = copy.deepcopy(self.tags)
        vpc.tags.append({
            "Key": "Name",
            "Value": self.configuration.vpc_name
        })
        self.aws_api.provision_vpc(vpc)
        self._vpc = vpc
        return vpc

    def provision_subnets(self):
        """
        Provision VPC subnets.

        :return:
        """

        all_zones = self.aws_api.ec2_client.get_all_availability_zones(region=self.region)
        valid_availability_zones = [zone for zone in all_zones if zone.zone_type == "availability-zone"]
        if len(valid_availability_zones) < self.configuration.availability_zones_count:
            raise ValueError(
                f"Not enough availability zones: needs {self.configuration.availability_zones_count} found only {len(valid_availability_zones)}")

        vpc_cidr_address = IP(self.configuration.vpc_cidr_block)
        vpc_subnets = vpc_cidr_address.split(self.configuration.subnet_mask_length)
        availability_zones = valid_availability_zones[:self.configuration.availability_zones_count]

        if len(vpc_subnets) < self.configuration.availability_zones_count * 2:
            raise RuntimeError(
                "Available VPC subnets do not cover the required for private and public subnets")

        public_subnet_index = len(vpc_subnets) // 2

        subnets = []
        for az_counter, availability_zone in enumerate(availability_zones):
            private_subnet_az_cidr = vpc_subnets[az_counter].str_address_slash_short_mask()
            public_subnet_az_cidr = vpc_subnets[public_subnet_index + az_counter].str_address_slash_short_mask()

            # private
            private_subnet_az = Subnet({})
            private_subnet_az.cidr_block = private_subnet_az_cidr
            private_subnet_az.vpc_id = self.vpc.id
            private_subnet_az.availability_zone_id = availability_zone.id
            private_subnet_az.region = Region.get_region(self.configuration.region)

            private_subnet_az.tags = copy.deepcopy(self.tags)
            private_subnet_az.tags.append({
                "Key": "Name",
                "Value": self.configuration.private_subnet_name_template.format(private_subnet_az.availability_zone_id)
            })
            subnets.append(private_subnet_az)

            # public
            public_subnet_az = Subnet({})
            public_subnet_az.cidr_block = public_subnet_az_cidr
            public_subnet_az.vpc_id = self.vpc.id
            public_subnet_az.availability_zone_id = availability_zone.id
            public_subnet_az.region = Region.get_region(self.configuration.region)

            public_subnet_az.tags = copy.deepcopy(self.tags)
            public_subnet_az.tags.append({
                "Key": "Name",
                "Value": self.configuration.public_subnet_name_template.format(public_subnet_az.availability_zone_id)
            })
            subnets.append(public_subnet_az)

        self.aws_api.provision_subnets(subnets)
        return subnets

    def provision_ecr_repository(self):
        """
        Create or update the ECR repo

        :return:
        """

        repo = ECRRepository({})
        repo.region = self.region
        repo.name = self.configuration.ecr_repository_name
        repo.tags = copy.deepcopy(self.tags)
        repo.tags.append({
            "Key": "Name",
            "Value": repo.name
        })

        repo.tags.append({
            "Key": self.configuration.infrastructure_last_update_time_tag,
            "Value": datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
        })
        self.aws_api.provision_ecr_repository(repo)
        return repo

    def provision_security_groups(self):
        """
        Provision all security groups.

        :return:
        """
        security_group = EC2SecurityGroup({})
        security_group.vpc_id = self.vpc.id
        security_group.name = self.configuration.db_rds_security_group_name
        security_group.description = f"Postgres {self.configuration.project_name} {self.configuration.environment_name}"
        security_group.region = self.region
        security_group.tags = copy.deepcopy(self.tags)
        security_group.tags.append({
            "Key": "Name",
            "Value": security_group.name
        })

        self.aws_api.provision_security_group(security_group, provision_rules=False)
        return security_group

    def provision_db_cluster_components(self):
        """
        Provision Postrgres cluster

        :return:
        """

        self.provision_rds_db_cluster_parameter_group()
        self.provision_rds_subnet_group()

        self.provision_rds_cluster()
        #self.provision_rds_db_instances()
        #self.change_password()
        #self.provision_rds_dns_name()

    def provision_db(self):
        """
        Provision DB.

        :return:
        """

        self.provision_rds_subnet_group()
        self.provision_rds_db_instance_parameter_group()
        self.provision_rds_instance()

    def provision_rds_instance(self):
        """
        Provision all the instances.

        :return:
        """
        aurora_engine_default_version = self.aws_api.rds_client.get_default_engine_version(self.region, self.configuration.db_type)["EngineVersion"]

        for counter in range(self.configuration.db_instance_count):
            db_instance = RDSDBInstance({})
            db_instance.region = self.region

            db_instance.id = self.configuration.db_rds_instance_id_template.format(counter=counter)
            db_instance.db_instance_class = "db.t3.micro"

            #db_instance.db_cluster_identifier = self.configuration.db_rds_cluster_identifier
            db_instance.db_subnet_group_name = self.configuration.db_rds_subnet_group_name
            db_instance.db_parameter_group_name = self.configuration.db_rds_instance_parameter_group_name
            db_instance.engine = \
            self.aws_api.rds_client.get_default_engine_version(self.region, self.configuration.db_type)["Engine"]
            db_instance.engine_version = aurora_engine_default_version

            db_instance.preferred_maintenance_window = "sun:03:30-sun:04:00"
            db_instance.storage_encrypted = True
            db_instance.allocated_storage = 20
            db_instance.max_allocated_storage = 100
            db_instance.preferred_backup_window = "09:23-09:53"
            db_instance.preferred_maintenance_window = "sun:03:30-sun:04:00"

            db_instance.copy_tags_to_snapshot = True

            db_instance.tags = copy.deepcopy(self.tags)
            db_instance.tags.append({
                "Key": "name",
                "Value": db_instance.id
            }
            )
            db_instance.master_username = "lion"
            db_instance.master_user_password = "admin123456!"
            self.aws_api.provision_db_instance(db_instance)
        return True

    def provision_rds_db_cluster_parameter_group(self):
        """
        Provision params.

        :return:
        """
        db_cluster_parameter_group = RDSDBClusterParameterGroup({})
        db_cluster_parameter_group.region = self.region
        db_cluster_parameter_group.name = self.configuration.db_rds_cluster_parameter_group_name
        db_cluster_parameter_group.db_parameter_group_family = self.aws_api.rds_client.get_default_engine_version(self.region, self.configuration.db_type)["DBParameterGroupFamily"]
        db_cluster_parameter_group.description = self.configuration.db_rds_cluster_parameter_group_description
        db_cluster_parameter_group.tags = copy.deepcopy(self.tags)
        db_cluster_parameter_group.tags.append({
            "Key": "name",
            "Value": db_cluster_parameter_group.name
        })

        return self.aws_api.provision_db_cluster_parameter_group(db_cluster_parameter_group)

    def provision_rds_db_instance_parameter_group(self):
        """
        Database param group.

        :return:
        """

        db_parameter_group = RDSDBParameterGroup({})
        db_parameter_group.region = self.region
        db_parameter_group.name = self.configuration.db_rds_instance_parameter_group_name
        db_parameter_group.db_parameter_group_family = self.aws_api.rds_client.get_default_engine_version(self.region, self.configuration.db_type)["DBParameterGroupFamily"]
        db_parameter_group.description = self.configuration.db_rds_parameter_group_description
        db_parameter_group.tags = copy.deepcopy(self.tags)
        db_parameter_group.tags.append({
            "Key": "name",
            "Value": db_parameter_group.name
        }
        )

        self.aws_api.provision_db_parameter_group(db_parameter_group)
        return True

    def provision_rds_subnet_group(self):
        """
        Subnets used by the cluster.

        :return:
        """

        subnet_group = RDSDBSubnetGroup({})
        subnet_group.region = self.region
        subnet_group.name = self.configuration.db_rds_subnet_group_name
        subnet_group.db_subnet_group_description = self.configuration.db_rds_subnet_group_description
        subnet_group.subnet_ids = [subnet.id for subnet in self.subnets if "private" in subnet.get_tagname()]
        subnet_group.tags = copy.deepcopy(self.tags)
        subnet_group.tags.append({
            "Key": "name",
            "Value": subnet_group.name
        }
        )
        return self.aws_api.provision_db_subnet_group(subnet_group)

    def provision_rds_cluster(self, snapshot=None):
        """
        Provision the cluster itself.

        :param snapshot:
        :return:
        """

        db_rds_security_group = self.aws_api.get_security_group_by_vpc_and_name(self.vpc,
                                                                                self.configuration.db_rds_security_group_name)

        aurora_engine_default_version = self.aws_api.rds_client.get_default_engine_version(self.region, self.configuration.db_type)["EngineVersion"]

        cluster = RDSDBCluster({})
        cluster.region = self.region
        cluster.db_subnet_group_name = self.configuration.db_rds_subnet_group_name
        cluster.db_cluster_parameter_group_name = self.configuration.db_rds_cluster_parameter_group_name
        cluster.backup_retention_period = 7
        cluster.database_name = self.configuration.db_rds_database_name
        cluster.id = self.configuration.db_rds_cluster_identifier
        cluster.vpc_security_group_ids = [db_rds_security_group.id]
        cluster.engine = self.aws_api.rds_client.get_default_engine_version(self.region, self.configuration.db_type)["Engine"]
        cluster.engine_version = aurora_engine_default_version
        cluster.port = 5432

        cluster.master_username = "admin"
        cluster.master_user_password = "admin123456!"
        cluster.preferred_backup_window = "09:23-09:53"
        cluster.preferred_maintenance_window = "sun:03:30-sun:04:00"
        cluster.storage_encrypted = True
        #cluster.allocated_storage = 1
        #cluster.db_cluster_instance_class = "db.t3.medium"
        cluster.engine_mode = "provisioned"

        cluster.deletion_protection = False
        cluster.copy_tags_to_snapshot = True
        cluster.enable_cloudwatch_logs_exports = [
            "audit",
            "error",
            "general",
            "slowquery"
        ]

        cluster.tags = copy.deepcopy(self.tags)
        cluster.tags.append({
            "Key": "name",
            "Value": cluster.id
        }
        )
        self.aws_api.provision_rds_db_cluster(cluster, snapshot=snapshot)

    def login_to_ecr(self):
        """
        Login to ECR for Docker to be able to upload images.
        
        :return:
        """
        logger.info(f"Fetching ECR credentials for region {self.configuration.region}")
        credentials = self.aws_api.get_ecr_authorization_info(region=self.region)

        if len(credentials) != 1:
            raise ValueError("len(credentials) != 1")
        credentials = credentials[0]

        registry, username, password = credentials["proxy_host"], credentials["user_name"], credentials["decoded_token"]
        return self.docker_api.login(registry, username, password)

    def prepare_build_directory(self):
        """
        Copy source code to build directory

        :return:
        """

        os.makedirs(self.configuration.local_deployment_directory_path, exist_ok=True)
        shutil.rmtree(self.configuration.local_deployment_directory_path)
        source_code_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "source_code"))
        shutil.copytree(source_code_path, self.configuration.local_deployment_directory_path)
        return True

    def compose_image_tag(self, tag_value):
        """

        :param tag_value:
        :return:
        """

        return f"{self.aws_account}.dkr.ecr.{self.configuration.region}.amazonaws.com/{self.configuration.ecr_repository_name}:{tag_value}"

    def build(self):
        """
        Build the image.

        :return:
        """

        tags = [self.compose_image_tag("latest")]
        self.docker_api.build(self.configuration.local_deployment_directory_path, tags)
        return tags

    def build_and_upload(self):
        """
        Prepare build dir.
        Build the image.
        Login to ECR
        Upload to ECR.

        :return:
        """
        self.prepare_build_directory()
        image_tags = self.build()
        self.login_to_ecr()
        return self.docker_api.upload_images(image_tags)

    def update_component(self):
        """
        Update code and infrastructure.

        ECS + EC2:
        self.provision_ssh_key_pairs
        self.generate_user_data
        self.provision_launch_template
        self.provision_ecs_capacity_provider
        self.attach_capacity_provider_to_ecs_cluster
        self.provision_ecs_cluster
        self.update_auto_scaling_group_desired_count

        :return:
        """

        if self.configuration.provision_infrastructure:
            self.provision_infrastructure()

        return self.build_and_upload()

    def provision_ecs_cluster(self):
        """
        Provision the ECS cluster.

        :return:
        """

        cluster = ECSCluster({})
        cluster.settings = [
            {
                "name": "containerInsights",
                "value": "disabled"
            }
        ]
        cluster.name = self.configuration.cluster_name
        cluster.region = self.region
        cluster.tags = [{key.lower(): value for key, value in dict_tag.items()} for dict_tag in self.tags]
        cluster.tags.append({
            "key": "name",
            "value": cluster.name
        })

        cluster.configuration = {}
        self.aws_api.provision_ecs_cluster(cluster)

        return cluster

    def generate_environment_values(self):
        """
        Generate task env vars.

        :return:
        """

        return []

    def provision_roles(self):
        """
        Provision IAM roles.

        :return:
        """

        self.provision_ecs_task_execution_role()
        self.provision_ecs_task_role()
        return True

    def provision_ecs_task_execution_role(self):
        """
        Role used by ECS service task running on the container instance to manage containers.

        :return:
        """

        assume_role_doc = json.dumps({
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Principal": {
                "Service": "ecs-tasks.amazonaws.com"
              },
              "Action": "sts:AssumeRole",
              "Condition": {
            "ArnLike":{
            "aws:SourceArn": f"arn:aws:ecs:{self.configuration.region}:{self.aws_account}:*"
            },
            "StringEquals":{
               "aws:SourceAccount": self.aws_account
            }
         }
            }
          ]
        })

        iam_role = IamRole({})
        iam_role.assume_role_policy_document = assume_role_doc
        iam_role.name = self.configuration.ecs_task_execution_role_name
        iam_role.path = f"/{self.configuration.environment_level}/"
        iam_role.description = "ECS task role used to control containers lifecycle"
        iam_role.max_session_duration = 3600
        iam_role.tags = copy.deepcopy(self.tags)
        iam_role.tags.append({
            "Key": "name",
            "Value": iam_role.name
        })

        iam_role.managed_policies_arns = ["arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"]
        iam_role.path = f"/{self.configuration.environment_level}/"
        self.aws_api.provision_iam_role(iam_role)
        return iam_role

    def provision_ecs_task_role(self):
        """
        ECS task role.

        :return:
        """

        iam_role = IamRole({})
        iam_role.description = f"ECS task {self.configuration.project_name} {self.configuration.environment_name} backend"
        iam_role.name = self.configuration.ecs_task_role_name
        iam_role.path = f"/{self.configuration.environment_level}/"
        iam_role.max_session_duration = 12 * 60 * 60
        iam_role.assume_role_policy_document = json.dumps({
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

        iam_role.tags = copy.deepcopy(self.tags)
        iam_role.tags.append({
            "Key": "name",
            "Value": iam_role.name
        })
        iam_role.inline_policies = []
        iam_role.path = f"/{self.configuration.environment_level}/"
        self.aws_api.provision_iam_role(iam_role)
        return iam_role

    def provision_ecs_task_definition(self):
        """
        Provision task definition.

        :return:
        """

        environ_values = self.generate_environment_values()

        ecr_image_id = self.compose_image_tag("latest")

        ecs_task_definition = ECSTaskDefinition({})
        ecs_task_definition.region = self.region
        ecs_task_definition.family = f"{self.configuration.project_name}-backend"

        ecs_task_definition.tags = [{key.lower(): value for key, value in dict_tag.items()} for dict_tag in self.tags]
        ecs_task_definition.tags.append({
            "key": "Name",
            "value": ecs_task_definition.family
        })
        port_mappings = [
            {
                "containerPort": 80,
                "hostPort": 0,
                "protocol": "tcp"
            }
        ]

        log_config = {
            "logDriver": "json-file",
            "options": {
                "labels": f"{self.configuration.environment_name}",
                "max-size": "1g",
                "max-file": "3"
            }
        }

        ecs_task_definition.container_definitions = [{
            "name": ecs_task_definition.family,
            "image": ecr_image_id,
            "portMappings": port_mappings,
            "essential": True,
            "environment": environ_values,
            "logConfiguration": log_config
        }
        ]

        ecs_task_definition.container_definitions[0]["cpu"] = self.configuration.ecs_task_definition_cpu_reservation

        ecs_task_definition.container_definitions[0]["memoryReservation"] = self.configuration.ecs_task_definition_memory_reservation

        ecs_task_definition.task_role_arn = f"arn:aws:iam::{self.aws_account}:role/{self.configuration.environment_level}/{self.configuration.ecs_task_role_name}"
        ecs_task_definition.execution_role_arn = f"arn:aws:iam::{self.aws_account}:role/{self.configuration.environment_level}/{self.configuration.ecs_task_execution_role_name}"

        ecs_task_definition.cpu = str(self.configuration.ecs_task_definition_cpu_reservation)

        ecs_task_definition.memory = str(self.configuration.ecs_task_definition_memory_reservation)

        self.aws_api.provision_ecs_task_definition(ecs_task_definition)

        return ecs_task_definition

    def provision_infrastructure(self):
        """
        Provision all infrastructure parts.

        :return:
        """

        self.provision_vpc()
        self.provision_subnets()
        self.provision_ecr_repository()
        self.provision_security_groups()
        self.provision_db()

    def dispose(self):
        """
        Dispose the project.

        :return:
        """

        for counter in range(self.configuration.db_instance_count):
            db_instance = RDSDBInstance({})
            db_instance.region = self.region
            db_instance.skip_final_snapshot = True
            db_instance.id = self.configuration.db_rds_instance_id_template.format(counter=counter)
            self.aws_api.rds_client.dispose_db_instance(db_instance)

        subnet_group = RDSDBSubnetGroup({"name": self.configuration.db_rds_subnet_group_name})
        subnet_group.region = self.region
        self.aws_api.rds_client.dispose_db_subnet_group(subnet_group)

        #self.configuration.db_rds_cluster_parameter_group_name
        #self.configuration.db_rds_instance_parameter_group_name
        #self.configuration.ecs_task_role_name
        #self.configuration.ecs_task_execution_role_name
        #self.configuration.cluster_name
        #task_definition

        self.aws_api.ec2_client.dispose_subnets(self.subnets)

        security_group = self.aws_api.get_security_group_by_vpc_and_name(self.vpc,
                                                                         self.configuration.db_rds_security_group_name)
        self.aws_api.ec2_client.dispose_security_groups([security_group])

        self.aws_api.ec2_client.dispose_vpc(self.vpc)

        ecr_repository = ECRRepository({})
        ecr_repository.name = self.configuration.ecr_repository_name
        ecr_repository.region = self.configuration.region
        self.aws_api.ecr_client.dispose_repository(ecr_repository)

        return True
