"""
Lion King- infra as a code project from Horey )

"""
# pylint: disable= too-many-lines
import copy
import datetime
import json
import os
import shutil

from horey.h_logger import get_logger
from horey.docker_api.docker_api import DockerAPI
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_clients.ssm_client import SSMClient
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.aws_api.aws_services_entities.vpc import VPC
from horey.aws_api.aws_services_entities.subnet import Subnet
from horey.aws_api.aws_services_entities.ecr_repository import ECRRepository
from horey.aws_api.base_entities.region import Region
from horey.replacement_engine.replacement_engine import ReplacementEngine
from horey.network.ip import IP
from horey.common_utils.common_utils import CommonUtils

from horey.aws_api.aws_services_entities.rds_db_cluster import RDSDBCluster
from horey.aws_api.aws_services_entities.rds_db_instance import RDSDBInstance
from horey.aws_api.aws_services_entities.rds_db_parameter_group import RDSDBParameterGroup
from horey.aws_api.aws_services_entities.ec2_security_group import EC2SecurityGroup
from horey.aws_api.aws_services_entities.rds_db_cluster_parameter_group import RDSDBClusterParameterGroup
from horey.aws_api.aws_services_entities.rds_db_subnet_group import RDSDBSubnetGroup
from horey.aws_api.aws_services_entities.ecs_cluster import ECSCluster
from horey.aws_api.aws_services_entities.ecs_task_definition import ECSTaskDefinition
from horey.aws_api.aws_services_entities.ecs_service import ECSService
from horey.aws_api.aws_services_entities.iam_role import IamRole
from horey.aws_api.aws_services_entities.cloud_watch_log_group import CloudWatchLogGroup
from horey.aws_api.aws_services_entities.acm_certificate import ACMCertificate
from horey.aws_api.aws_services_entities.elbv2_load_balancer import LoadBalancer
from horey.aws_api.aws_services_entities.elbv2_target_group import ELBV2TargetGroup
from horey.aws_api.aws_services_entities.internet_gateway import InternetGateway
from horey.aws_api.aws_services_entities.route_table import RouteTable
from horey.aws_api.aws_services_entities.route53_hosted_zone import HostedZone
from horey.aws_api.aws_services_entities.ec2_instance import EC2Instance
from horey.aws_api.aws_services_entities.key_pair import KeyPair

logger = get_logger()


# pylint: disable= too-many-instance-attributes
class LionKing:
    """
    Main class.

    """

    def __init__(self, configuration):
        self.configuration = configuration
        self._aws_api = None
        self._replacement_engine = None
        self._docker_api = None
        self._region = None
        self._vpc = None
        self._subnets = None
        self._adminer_target_group = None
        self._grafana_target_group = None
        self._backend_target_group = None
        self._backend_security_group = None
        self._ecs_cluster = None

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
    def replacement_engine(self):
        """
        replacement_engine used for the deployment.

        :return:
        """
        if self._replacement_engine is None:
            self._replacement_engine = ReplacementEngine()
        return self._replacement_engine

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
                       subnet.get_tag("environment_name",
                                      ignore_missing_tag=True) == self.configuration.environment_name and \
                       subnet.get_tag("project_name", ignore_missing_tag=True) == self.configuration.project_name]

            if len(subnets) != self.configuration.availability_zones_count * 2:
                raise RuntimeError(
                    f"Looking for subnets. Expected:{self.configuration.availability_zones_count * 2:}, found: {len(subnets)}")

            self._subnets = subnets

        return self._subnets

    def find_target_group_by_name(self, name):
        """
        Find target group by tag name
        :return:
        """
        all_target_groups = self.aws_api.elbv2_client.get_region_target_groups(self.region)
        if not all_target_groups:
            return None
        target_groups = CommonUtils.find_objects_by_values(all_target_groups, {"name": name})
        if len(target_groups) > 1:
            raise RuntimeError(f"Found {len(target_groups)} target groups")
        if len(target_groups) == 0:
            return None

        return target_groups[0]

    @property
    def adminer_target_group(self):
        """
        Initialized object to reuse.

        :return:
        """
        if not self._adminer_target_group:
            self._adminer_target_group = self.find_target_group_by_name(self.configuration.target_group_adminer_name)
        return self._adminer_target_group

    @property
    def grafana_target_group(self):
        """
        Initialized object to reuse.

        :return:
        """
        if not self._grafana_target_group:
            self._grafana_target_group = self.find_target_group_by_name(self.configuration.target_group_grafana_name)
        return self._grafana_target_group

    @property
    def backend_target_group(self):
        """
        Initialized object to reuse.

        :return:
        """
        if not self._backend_target_group:
            self._backend_target_group = self.find_target_group_by_name(self.configuration.target_group_backend_name)
        return self._backend_target_group

    @property
    def backend_security_group(self):
        """
        Initialized object to reuse.

        :return:
        """
        if not self._backend_security_group:
            self._backend_security_group = self.aws_api.get_security_group_by_vpc_and_name(self.vpc,
                                                                                           self.configuration.backend_security_group_name)
        return self._backend_security_group

    @property
    def ecs_cluster(self):
        """
        Initialized object to reuse.

        :return:
        """

        if not self._ecs_cluster:
            self._ecs_cluster = ECSCluster({"name": self.configuration.cluster_name})
            self._ecs_cluster.region = self.region
            if not self.aws_api.ecs_client.update_cluster_information(self._ecs_cluster):
                raise RuntimeError(f"Was not able to find cluster {self.configuration.cluster_name}")
        return self._ecs_cluster

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

    def provision_routing(self):
        """
        Provision routing tables and gateways.

        :return:
        """

        internet_gateway = self.provision_internet_gateway()

        self.provision_public_route_tables(internet_gateway)
        return True

    def provision_internet_gateway(self):
        """
        Provision the main public router - gateway to the internet.

        :return:
        """
        inet_gateway = InternetGateway({})
        inet_gateway.attachments = [{"VpcId": self.vpc.id}]
        inet_gateway.region = self.region
        inet_gateway.tags = copy.deepcopy(self.tags)
        inet_gateway.tags.append({
            "Key": "Name",
            "Value": self.configuration.internet_gateway_name
        })

        self.aws_api.provision_internet_gateway(inet_gateway)

        return inet_gateway

    def provision_public_route_tables(self, internet_gateway):
        """
        Public subnets route tables.

        :param internet_gateway:
        :return:
        """

        public_subnets = [subnet for subnet in self.subnets if "public" in subnet.get_tagname()]
        # public
        for public_subnet in public_subnets:
            route_table = RouteTable({})
            route_table.region = self.region
            route_table.vpc_id = self.vpc.id
            route_table.associations = [{
                "SubnetId": public_subnet.id
            }]

            route_table.routes = [{
                "DestinationCidrBlock": "0.0.0.0/0",
                "GatewayId": internet_gateway.id
            }]

            route_table.tags = copy.deepcopy(self.tags)
            route_table.tags.append({
                "Key": "Name",
                "Value": self.configuration.route_table_template.format(public_subnet.get_tagname())
            })

            self.aws_api.provision_route_table(route_table)

    def provision_ecr_repositories(self):
        """
        All ECR repos used in the project.

        :return:
        """

        for name in [self.configuration.ecr_repository_backend_name,
                     self.configuration.ecr_repository_adminer_name,
                     self.configuration.ecr_repository_grafana_name]:
            self.provision_ecr_repository(name)
        return True

    def provision_ecr_repository(self, repo_name):
        """
        Create or update the ECR repo

        :return:
        """

        repo = ECRRepository({})
        repo.region = self.region
        repo.name = repo_name
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

        administrators_addresses = ["84.229.110.142/32"]
        administrator_ip_ranges = [{"CidrIp": address,
                                    "Description": f"Administrator access {address}"} for address in
                                   administrators_addresses]

        ret = []
        # Bastion
        security_group_bastion = EC2SecurityGroup({})
        security_group_bastion.vpc_id = self.vpc.id
        security_group_bastion.name = self.configuration.bastion_security_group_name
        security_group_bastion.description = f"Internet facing instance {self.configuration.project_name} {self.configuration.environment_name}"
        security_group_bastion.region = self.region
        security_group_bastion.tags = copy.deepcopy(self.tags)
        security_group_bastion.tags.append({
            "Key": "Name",
            "Value": security_group_bastion.name
        })
        security_group_bastion.ip_permissions = [
            {
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "IpRanges": administrator_ip_ranges,
                "Ipv6Ranges": [],
                "PrefixListIds": [],
                "UserIdGroupPairs": []
            }
        ]
        self.aws_api.provision_security_group(security_group_bastion, provision_rules=True)

        ret.append(security_group_bastion)

        # ALB
        security_group_alb = EC2SecurityGroup({})
        security_group_alb.vpc_id = self.vpc.id
        security_group_alb.name = self.configuration.public_load_balancer_security_group_name
        security_group_alb.description = f"Internet facing load balancer {self.configuration.project_name} {self.configuration.environment_name}"
        security_group_alb.region = self.region
        security_group_alb.tags = copy.deepcopy(self.tags)
        security_group_alb.tags.append({
            "Key": "Name",
            "Value": security_group_alb.name
        })
        security_group_alb.ip_permissions = [
            {
                "IpProtocol": "tcp",
                "FromPort": 444,
                "ToPort": 445,
                "IpRanges": administrator_ip_ranges,
                "Ipv6Ranges": [],
                "PrefixListIds": [],
                "UserIdGroupPairs": []
            },
            {
                "IpProtocol": "tcp",
                "FromPort": 443,
                "ToPort": 443,
                "IpRanges": [{"CidrIp": "0.0.0.0/0",
                              "Description": "Public access"}],
                "Ipv6Ranges": [],
                "PrefixListIds": [],
                "UserIdGroupPairs": []
            }
        ]
        self.aws_api.provision_security_group(security_group_alb, provision_rules=True)

        ret.append(security_group_alb)

        # Backend
        security_group = EC2SecurityGroup({})
        security_group.vpc_id = self.vpc.id
        security_group.name = self.configuration.backend_security_group_name
        security_group.description = f"Backend {self.configuration.project_name} {self.configuration.environment_name}"
        security_group.region = self.region
        security_group.tags = copy.deepcopy(self.tags)
        security_group.tags.append({
            "Key": "Name",
            "Value": security_group.name
        })
        ret.append(security_group)
        security_group.ip_permissions = [
            {
                "IpProtocol": "tcp",
                "FromPort": 0,
                "ToPort": 65535,
                "IpRanges": [],
                "Ipv6Ranges": [],
                "PrefixListIds": [],
                "UserIdGroupPairs": [
                    {
                        "GroupId": security_group_alb.id,
                        "UserId": self.aws_account,
                        "Description": "Access from public load balancer to ecs services"
                    }
                ]
            }
        ]
        self.aws_api.provision_security_group(security_group, provision_rules=True)
        self._backend_security_group = security_group

        # RDS
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

        security_group.ip_permissions = [
            {
                "IpProtocol": "tcp",
                "FromPort": 5432,
                "ToPort": 5432,
                "IpRanges": [],
                "Ipv6Ranges": [],
                "PrefixListIds": [],
                "UserIdGroupPairs": [
                    {
                        "GroupId": self.backend_security_group.id,
                        "UserId": self.aws_account,
                        "Description": "Access from ECS services to RDS"
                    },
                    {
                        "GroupId": security_group_bastion.id,
                        "UserId": self.aws_account,
                        "Description": "Access from the backbone to RDS"
                    }

                ]
            }
        ]
        self.aws_api.provision_security_group(security_group, provision_rules=True)

        return ret

    def provision_db_cluster_components(self):
        """
        Provision Postrgres cluster

        :return:
        """

        self.provision_rds_db_cluster_parameter_group()
        self.provision_rds_subnet_group()

        self.provision_rds_cluster()
        # self.provision_rds_db_instances()
        # self.change_password()
        # self.provision_rds_dns_name()

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

        for counter in range(self.configuration.db_instance_count):
            db_instance = RDSDBInstance({})
            db_instance.region = self.region

            db_instance.id = self.configuration.db_rds_instance_id_template.format(counter=counter)
            db_instance.db_instance_class = "db.t3.micro"

            # db_instance.db_cluster_identifier = self.configuration.db_rds_cluster_identifier
            db_instance.db_subnet_group_name = self.configuration.db_rds_subnet_group_name
            db_instance.db_parameter_group_name = self.configuration.db_rds_instance_parameter_group_name
            db_instance.engine = \
                self.aws_api.rds_client.get_engine_version(self.region, self.configuration.db_type,
                                                           self.configuration.db_engine_version)["Engine"]
            db_instance.engine_version = self.configuration.db_engine_version
            db_instance.vpc_security_group_ids = [self.aws_api.get_security_group_by_vpc_and_name(self.vpc,
                                                                                                  self.configuration.db_rds_security_group_name).id]

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
            db_instance.db_name = self.configuration.db_rds_database_name
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
        db_cluster_parameter_group.db_parameter_group_family = \
            self.aws_api.rds_client.get_engine_version(self.region, self.configuration.db_type,
                                                       self.configuration.db_engine_version)[
                "DBParameterGroupFamily"]
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
        db_parameter_group.db_parameter_group_family = \
            self.aws_api.rds_client.get_engine_version(self.region, self.configuration.db_type,
                                                       self.configuration.db_engine_version)[
                "DBParameterGroupFamily"]
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

        aurora_engine_default_version = \
            self.aws_api.rds_client.get_engine_version(self.region, self.configuration.db_type,
                                                       self.configuration.db_engine_version)["EngineVersion"]

        cluster = RDSDBCluster({})
        cluster.region = self.region
        cluster.db_subnet_group_name = self.configuration.db_rds_subnet_group_name
        cluster.db_cluster_parameter_group_name = self.configuration.db_rds_cluster_parameter_group_name
        cluster.backup_retention_period = 7
        cluster.database_name = self.configuration.db_rds_database_name
        cluster.id = self.configuration.db_rds_cluster_identifier
        cluster.vpc_security_group_ids = [db_rds_security_group.id]
        cluster.engine = self.aws_api.rds_client.get_engine_version(self.region, self.configuration.db_type,
                                                                    self.configuration.db_engine_version)[
            "Engine"]
        cluster.engine_version = aurora_engine_default_version
        cluster.port = 5432

        cluster.master_username = "admin"
        cluster.master_user_password = "admin123456!"
        cluster.preferred_backup_window = "09:23-09:53"
        cluster.preferred_maintenance_window = "sun:03:30-sun:04:00"
        cluster.storage_encrypted = True
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

    def provision_cloudwatch_log_groups(self):
        """
        All cloudwatch log groups

        :return:
        """

        self.provision_cloudwatch_log_group(self.configuration.cloudwatch_log_group_name_adminer)
        self.provision_cloudwatch_log_group(self.configuration.cloudwatch_log_group_name_grafana)
        self.provision_cloudwatch_log_group(self.configuration.cloudwatch_log_group_name_backend, retention=60)
        return True

    def provision_cloudwatch_log_group(self, name, retention=1):
        """
        Retention in days.

        :param name:
        :param retention:
        :return:
        """
        log_group = CloudWatchLogGroup({})
        log_group.region = self.region
        log_group.retention_in_days = retention
        log_group.name = name
        log_group.tags = {tag["Key"]: tag["Value"] for tag in self.tags}
        log_group.tags["name"] = log_group.name
        self.aws_api.provision_cloudwatch_log_group(log_group)
        return True

    def provision_load_balancer(self):
        """
        Provision the ELB in AWS

        :return:
        """

        all_public_subnets = [subnet for subnet in self.subnets if "public" in subnet.get_tagname()]

        public_subnet_to_az_map = {public_subnet.availability_zone: public_subnet.id for public_subnet in
                                   all_public_subnets}

        all_private_subnets = [subnet for subnet in self.subnets if "private" in subnet.get_tagname()]
        private_subnet_to_az_map = [private_subnet.availability_zone for private_subnet in all_private_subnets]

        public_subnets_ids = [public_subnet_id for public_subnet_az, public_subnet_id in public_subnet_to_az_map.items()
                              if public_subnet_az in private_subnet_to_az_map]

        load_balancer = LoadBalancer({})
        load_balancer.name = self.configuration.load_balancer_name
        load_balancer.subnets = public_subnets_ids
        load_balancer.scheme = "internet-facing"
        load_balancer.region = self.region

        load_balancer.tags = copy.deepcopy(self.tags)
        load_balancer.tags.append({
            "Key": "Name",
            "Value": load_balancer.name
        })
        load_balancer.type = "application"
        load_balancer.ip_address_type = "ipv4"

        security_group = self.aws_api.get_security_group_by_vpc_and_name(self.vpc,
                                                                         self.configuration.public_load_balancer_security_group_name)
        load_balancer.security_groups = [security_group.id]
        self.aws_api.provision_load_balancer(load_balancer)
        return load_balancer

    def provision_load_balancer_target_groups(self):
        """
        LB target groups.
        :return:
        """

        self._adminer_target_group = self.provision_load_balancer_target_group(
            self.configuration.target_group_adminer_name, 8080)
        self._grafana_target_group = self.provision_load_balancer_target_group(
            self.configuration.target_group_grafana_name, 3000)
        self._backend_target_group = self.provision_load_balancer_target_group(
            self.configuration.target_group_backend_name, 80)

    def provision_load_balancer_target_group(self, name, port):
        """
        Provision default target group.

        :param name:
        :param port:
        :return:
        """

        target_group = ELBV2TargetGroup({})
        target_group.region = self.region
        target_group.name = name
        target_group.protocol = "HTTP"
        target_group.port = port
        target_group.vpc_id = self.vpc.id

        target_group.health_check_protocol = "HTTP"
        target_group.health_check_port = "traffic-port"

        target_group.health_check_enabled = True
        target_group.health_check_interval_seconds = 30
        target_group.health_check_timeout_seconds = 5
        target_group.healthy_threshold_count = 2
        target_group.unhealthy_threshold_count = 4

        target_group.health_check_path = "/"
        target_group.target_type = "ip"
        target_group.tags = copy.deepcopy(self.tags)
        target_group.tags.append({
            "Key": "Name",
            "Value": target_group.name
        })

        self.aws_api.provision_load_balancer_target_group(target_group)
        return target_group

    def provision_certificate(self):
        """
        Provision global certificate for this environment.

        :return:
        """

        cert = ACMCertificate({})
        cert.region = self.region
        cert.domain_name = self.configuration.public_hosted_zone_name
        cert.subject_alternative_names = [f"*.{self.configuration.public_hosted_zone_name}"]
        cert.validation_method = "DNS"
        cert.tags = copy.deepcopy(self.tags)
        cert.tags.append({
            "Key": "name",
            "Value": cert.domain_name.replace("*", "star")
        })

        self.aws_api.provision_acm_certificate(cert, self.configuration.public_hosted_zone_name)
        return cert

    def provision_load_balancer_listeners(self, load_balancer):
        """
        Provision all listeners

        :return:
        """
        domain_name = self.configuration.public_hosted_zone_name
        cert_name = domain_name.replace("*", "star")
        certificate = self.aws_api.acm_client.get_certificate_by_tags(self.region, {"name": cert_name},
                                                                      ignore_missing_tag=True)

        self.provision_load_balancer_listener(load_balancer, 444, self.adminer_target_group, certificate)
        self.provision_load_balancer_listener(load_balancer, 445, self.grafana_target_group, certificate)
        self.provision_load_balancer_listener(load_balancer, 443, self.backend_target_group, certificate)

    def provision_load_balancer_listener(self, load_balancer, port, target_group, certificate):
        """
        Listeners and rules.

        :return:
         """

        # listener
        listener = LoadBalancer.Listener({})
        listener.protocol = "HTTPS"
        listener.ssl_policy = "ELBSecurityPolicy-TLS13-1-2-2021-06"
        listener.certificates = [
            {
                "CertificateArn": certificate.arn
            }
        ]

        listener.port = port
        listener.default_actions = [{"Type": "forward",
                                     "TargetGroupArn": target_group.arn}]

        listener.load_balancer_arn = load_balancer.arn
        listener.region = self.region

        self.aws_api.provision_load_balancer_listener(listener)

    def provision_load_balancer_components(self):
        """
        Provision load balancer and all its submodules.

        :return:
        """

        load_balancer = self.provision_load_balancer()
        self.provision_load_balancer_target_groups()
        self.provision_load_balancer_listeners(load_balancer)
        self.provision_load_balancer_public_domain_name(load_balancer)

        return load_balancer

    def provision_load_balancer_public_domain_name(self, load_balancer):
        """
        Provision public Route53 hosted zone and relevant records.

        :return:
        """

        hosted_zone = HostedZone({})
        hosted_zone.name = self.configuration.public_hosted_zone_name
        dict_record = {
            "Name": f"app.{hosted_zone.name}",
            "Type": "CNAME",
            "TTL": 300,
            "ResourceRecords": [
                {
                    "Value": load_balancer.dns_name
                }
            ]}

        record = HostedZone.Record(dict_record)
        hosted_zone.records.append(record)
        dict_record = {
            "Name": f"{hosted_zone.name}",
            "Type": "A",
            "AliasTarget": {
                "HostedZoneId": "Z215JYRZR1TBD5",
                "DNSName": load_balancer.dns_name,
                "EvaluateTargetHealth": True
            }
        }

        record = HostedZone.Record(dict_record)
        hosted_zone.records.append(record)
        self.aws_api.provision_hosted_zone(hosted_zone)

    def provision_grafana_postgres_db(self):
        """
        Provision database parts for grafana HA database.
        postgres=# CREATE USER grafana_user WITH LOGIN NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
        CREATE ROLE
        postgres=# ALTER ROLE grafana_user WITH PASSWORD 'Aa123456!';
        ALTER ROLE
        postgres=# CREATE DATABASE grafana WITH OWNER = grafana_user ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8' TABLESPACE = pg_default CONNECTION LIMIT = -1;
        CREATE DATABASE
        :return:

        """

    def provision_adminer(self):
        """
        Postgres manager.
        docker run -p 9090:9090 lion_king_adminer:latest

        You can specify the default host with the ADMINER_DEFAULT_SERVER environment variable.
        This is useful if you are connecting to an external server or a docker container named something other than
        the default db.

        :return:
        """

        os.makedirs(self.configuration.local_deployment_directory_path, exist_ok=True)
        shutil.rmtree(self.configuration.local_deployment_directory_path)
        source_code_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "adminer"))
        shutil.copytree(source_code_path, self.configuration.local_deployment_directory_path)

        image_tags = [self.compose_image_tag(self.configuration.ecr_repository_adminer_name, "latest")]
        self.docker_api.build(self.configuration.local_deployment_directory_path, image_tags)

        self.login_to_ecr()

        self.docker_api.upload_images(image_tags)
        task_definition_family = self.configuration.ecs_task_definition_family_adminer
        environ_values = self.generate_environment_values()
        log_group_name = self.configuration.cloudwatch_log_group_name_adminer
        container_name = "adminer"
        container_port = 8080
        ecs_task_definition = self.provision_ecs_task_definition(image_tags[0], environ_values, task_definition_family,
                                                                 container_port,
                                                                 log_group_name, container_name)
        self.provision_ecs_service(self.configuration.ecs_service_name_adminer, self.ecs_cluster, ecs_task_definition,
                                   self.adminer_target_group, self.backend_security_group)

    def provision_grafana(self):
        """
        Provision grafana components.
        environ_values = [
            {"name": "GF_SECURITY_ADMIN_USER",
             "value": "mufasa"
             },
            {"name": "GF_SECURITY_ADMIN_PASSWORD",
             "value": "Aa123456!"
             }
        ]

        :return:
        """

        self.provision_grafana_postgres_db()

        os.makedirs(self.configuration.local_deployment_directory_path, exist_ok=True)
        shutil.rmtree(self.configuration.local_deployment_directory_path)
        source_code_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "grafana"))
        shutil.copytree(source_code_path, self.configuration.local_deployment_directory_path)
        self.replacement_engine.perform_recursive_replacements(self.configuration.local_deployment_directory_path,
                                                               {
                                                                   "STRING_REPLACEMENT_GRAFANA_DB_HOST": self.configuration.grafana_db_host_private_address,
                                                                   "STRING_REPLACEMENT_GRAFANA_DB_NAME": "grafana",
                                                                   "STRING_REPLACEMENT_GRAFANA_DB_USERNAME": "grafana_user",
                                                                   "STRING_REPLACEMENT_GRAFANA_DB_PASSWORD": "Aa123456!"})

        tags = ["grafana:latest"]
        self.docker_api.build(self.configuration.local_deployment_directory_path, tags)

        image_tags = self.build()
        self.login_to_ecr()

        return self.docker_api.upload_images(image_tags)

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

    def compose_image_tag(self, repo_name, tag_value):
        """

        :param repo_name:
        :param tag_value:
        :return:
        """

        return f"{self.aws_account}.dkr.ecr.{self.configuration.region}.amazonaws.com/{repo_name}:{tag_value}"

    def build(self):
        """
        Build the image.

        :return:
        """

        tags = [self.compose_image_tag(self.configuration.ecr_repository_backend_name, "latest")]
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
        self.docker_api.upload_images(image_tags)
        return image_tags

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

        image_tags = self.build_and_upload()
        task_definition_family = self.configuration.ecs_task_definition_family_backend
        environ_values = self.generate_environment_values()
        log_group_name = self.configuration.cloudwatch_log_group_name_backend
        container_name = "backend"
        container_port = 80
        ecs_task_definition = self.provision_ecs_task_definition(image_tags[0], environ_values, task_definition_family,
                                                                 container_port,
                                                                 log_group_name, container_name)
        self.provision_ecs_service(self.configuration.ecs_service_name_backend, self.ecs_cluster, ecs_task_definition,
                                   self.backend_target_group, self.backend_security_group)
        return True

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
        self._ecs_cluster = cluster

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
                        "ArnLike": {
                            "aws:SourceArn": f"arn:aws:ecs:{self.configuration.region}:{self.aws_account}:*"
                        },
                        "StringEquals": {
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

    # pylint: disable= too-many-arguments
    def provision_ecs_task_definition(self, ecr_image_id, environ_values, task_definition_family, container_port,
                                      log_group_name, container_name):
        """
        Provision task definition.

        :return:
        """

        ecs_task_definition = ECSTaskDefinition({})
        ecs_task_definition.region = self.region
        ecs_task_definition.family = task_definition_family

        ecs_task_definition.tags = [{key.lower(): value for key, value in dict_tag.items()} for dict_tag in self.tags]
        ecs_task_definition.tags.append({
            "key": "Name",
            "value": ecs_task_definition.family
        })
        port_mappings = [
            {
                "containerPort": container_port,
                "hostPort": container_port,
                "protocol": "tcp"
            }
        ]

        log_config = {
            "logDriver": "awslogs",
            "options": {
                "awslogs-group": log_group_name,
                "awslogs-region": self.configuration.region,
                "awslogs-stream-prefix": "ecs"
            }
        }

        ecs_task_definition.container_definitions = [{
            "name": container_name,
            "image": ecr_image_id,
            "portMappings": port_mappings,
            "essential": True,
            "environment": environ_values,
            "logConfiguration": log_config
        }
        ]

        ecs_task_definition.container_definitions[0]["cpu"] = self.configuration.ecs_task_definition_cpu_reservation

        ecs_task_definition.container_definitions[0][
            "memoryReservation"] = self.configuration.ecs_task_definition_memory_reservation

        ecs_task_definition.task_role_arn = f"arn:aws:iam::{self.aws_account}:role/{self.configuration.environment_level}/{self.configuration.ecs_task_role_name}"
        ecs_task_definition.execution_role_arn = f"arn:aws:iam::{self.aws_account}:role/{self.configuration.environment_level}/{self.configuration.ecs_task_execution_role_name}"

        ecs_task_definition.cpu = str(self.configuration.ecs_task_definition_cpu_reservation)
        ecs_task_definition.requires_compatibilities = ["FARGATE"]
        ecs_task_definition.network_mode = "awsvpc"

        ecs_task_definition.memory = str(self.configuration.ecs_task_definition_memory_reservation)
        ecs_task_definition.runtime_platform = {
            "cpuArchitecture": "ARM64",
            "operatingSystemFamily": "LINUX"
        }

        self.aws_api.provision_ecs_task_definition(ecs_task_definition)

        return ecs_task_definition

    # pylint: disable= too-many-arguments
    def provision_ecs_service(self, service_name, ecs_cluster, ecs_task_definition, alb_target_group, security_group):
        """
        Provision component's ECS service.

        :param service_name:
        :param ecs_cluster:
        :param ecs_task_definition:
        :param alb_target_group:
        :param security_group:
        :return:
        """

        ecs_service = ECSService({})
        ecs_service.name = service_name
        ecs_service.region = self.region

        ecs_service.tags = [{key.lower(): value for key, value in dict_tag.items()} for dict_tag in self.tags]
        ecs_service.tags.append({
            "key": "Name",
            "value": ecs_service.name
        })

        ecs_service.cluster_arn = ecs_cluster.arn
        ecs_service.task_definition = ecs_task_definition.arn

        ecs_service.load_balancers = [{
            "targetGroupArn": alb_target_group.arn,
            "containerName": ecs_task_definition.container_definitions[0]["name"],
            "containerPort": ecs_task_definition.container_definitions[0]["portMappings"][0]["containerPort"]
        }]

        ecs_service.desired_count = 1

        ecs_service.launch_type = "FARGATE"
        ecs_service.network_configuration = {
            "awsvpcConfiguration": {
                "subnets": [subnet.id for subnet in self.subnets if "public" in subnet.get_tagname()],
                "securityGroups": [security_group.id],
                "assignPublicIp": "ENABLED"
            }
        }

        ecs_service.deployment_configuration = {
            "deploymentCircuitBreaker": {
                "enable": False,
                "rollback": False
            },
            "maximumPercent": 200,
            "minimumHealthyPercent": 100
        }

        ecs_service.health_check_grace_period_seconds = 10
        ecs_service.scheduling_strategy = "REPLICA"
        ecs_service.enable_ecs_managed_tags = False
        ecs_service.enable_execute_command = False

        wait_timeout = 10 * 60
        logger.info(f"Starting ECS service deployment with {wait_timeout=}")
        self.aws_api.provision_ecs_service(ecs_service, wait_timeout=wait_timeout)

    def get_bastion_ami(self):
        """
        Find bastion ami

        :return:
        """
        client = SSMClient()
        param = client.get_region_parameter(self.configuration.region,
                                            "/aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp2/ami-id")

        filter_request = {"ImageIds": [param.value]}
        amis = self.aws_api.ec2_client.get_region_amis(self.region, custom_filters=filter_request)
        if len(amis) != 1:
            raise RuntimeError(f"Can not find single AMI using filter: {filter_request['Filters']}")
        return amis[0]

    def provision_bastion_ssh_key_pair(self):
        """
        Provision Bastion SSH Key-pair.

        :return:
        """

        key_pair = KeyPair({})
        key_pair.name = self.configuration.bastion_ssh_key_pair_name
        key_pair.key_type = "ed25519"
        key_pair.region = Region.get_region(self.configuration.region)
        key_pair.tags = copy.deepcopy(self.tags)
        key_pair.tags.append({
            "Key": "Name",
            "Value": key_pair.name
        })

        self.aws_api.provision_key_pair(key_pair, save_to_secrets_manager=True, secrets_manager_region=self.region)

        return key_pair

    def provision_bastion_instance(self):
        """
        Provision instance used as a gateway.

        :return:
        """

        security_group = self.aws_api.get_security_group_by_vpc_and_name(self.vpc,
                                                                         self.configuration.bastion_security_group_name)
        self.provision_bastion_ssh_key_pair()

        ami = self.get_bastion_ami()

        target = EC2Instance({})
        target.image_id = ami.id
        target.instance_type = "t2.micro"

        target.key_name = self.configuration.bastion_ssh_key_pair_name
        target.region = self.region
        target.min_count = 1
        target.max_count = 1

        target.tags = copy.deepcopy(self.tags)
        target.tags.append({
            "Key": "Name",
            "Value": self.configuration.bastion_instance_name
        })

        target.ebs_optimized = True
        target.instance_initiated_shutdown_behavior = "terminate"

        target.network_interfaces = [
            {
                "AssociatePublicIpAddress": True,
                "DeleteOnTermination": True,
                "Description": "Primary network interface",
                "DeviceIndex": 0,
                "Groups": [
                    security_group.id
                ],
                "Ipv6AddressCount": 0,
                "SubnetId": [subnet for subnet in self.subnets if "public" in subnet.get_tagname()][0].id,
                "InterfaceType": "interface",
            }
        ]

        target.block_device_mappings = [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "VolumeSize": 8,
                    "VolumeType": "gp3",
                },
            }
        ]
        target.monitoring = {"Enabled": False}

        self.aws_api.provision_ec2_instance(target)
        return target

    def provision_infrastructure(self):
        """
        Provision all infrastructure parts.

        :return:
        """

        self.provision_vpc()
        self.provision_subnets()
        self.provision_routing()
        self.provision_ecr_repositories()
        self.provision_security_groups()
        self.provision_roles()
        self.provision_db()
        self.provision_cloudwatch_log_groups()
        self.provision_ecs_cluster()
        self.provision_certificate()
        self.provision_load_balancer_components()
        self.provision_adminer()
        # self.provision_grafana()

    def dispose(self):
        """
        Dispose the project.

        :return:
        """
        self.dispose_db_components()
        cluster = ECSCluster({"name": self.configuration.cluster_name})
        cluster.region = self.region
        service = ECSService({"name": self.configuration.ecs_service_name_backend})
        service.region = self.region
        self.aws_api.ecs_client.dispose_service(cluster, service)
        self.aws_api.ecs_client.dispose_cluster(cluster)

        load_balancer = LoadBalancer({})
        load_balancer.region = self.region
        load_balancer.name = self.configuration.load_balancer_name
        self.aws_api.elbv2_client.dispose_load_balancer(load_balancer)

        for target_group in [self.grafana_target_group, self.backend_target_group, self.adminer_target_group]:
            self.aws_api.elbv2_client.dispose_target_group_raw(target_group.generate_dispose_request())

        inet_gateway = InternetGateway({})
        inet_gateway.region = self.region
        inet_gateway.name = self.configuration.internet_gateway_name
        inet_gateway.tags = copy.deepcopy(self.tags)
        inet_gateway.tags.append({
            "Key": "Name",
            "Value": self.configuration.internet_gateway_name
        })
        self.aws_api.ec2_client.dispose_internet_gateway(inet_gateway)

        iam_role = IamRole({})
        iam_role.name = self.configuration.ecs_task_role_name
        iam_role.path = f"/{self.configuration.environment_level}/"
        self.aws_api.iam_client.dispose_role(iam_role, detach_policies=True)

        iam_role = IamRole({})
        iam_role.name = self.configuration.ecs_task_execution_role_name
        iam_role.path = f"/{self.configuration.environment_level}/"
        self.aws_api.iam_client.dispose_role(iam_role, detach_policies=True)

        ret = self.aws_api.ecs_client.get_all_task_definitions(region=self.region)
        for task_definition in ret:
            if task_definition.family == self.configuration.ecs_task_definition_family_backend:
                self.aws_api.ecs_client.dispose_task_definition(task_definition)

        log_group = CloudWatchLogGroup({})
        log_group.region = self.region
        log_group.name = self.configuration.cloudwatch_log_group_name
        self.aws_api.cloud_watch_logs_client.dispose_log_group(log_group)

        self.aws_api.ec2_client.dispose_subnets(self.subnets)
        # self.aws_api.ec2_client.dispose_route_tables(route_tables)

        security_group = self.aws_api.get_security_group_by_vpc_and_name(self.vpc,
                                                                         self.configuration.db_rds_security_group_name)
        self.aws_api.ec2_client.dispose_security_groups([security_group])
        for name in [self.configuration.ecr_repository_backend_name,
                     self.configuration.ecr_repository_adminer_name,
                     self.configuration.ecr_repository_grafana_name]:
            ecr_repository = ECRRepository({})
            ecr_repository.name = name
            ecr_repository.region = self.configuration.region
            self.aws_api.ecr_client.dispose_repository(ecr_repository)

        self.aws_api.ec2_client.dispose_vpc(self.vpc)

        return True

    def dispose_db_components(self):
        """
        Dispose all RDS related components.

        :return:
        """

        for counter in range(self.configuration.db_instance_count):
            db_instance = RDSDBInstance({})
            db_instance.region = self.region
            db_instance.skip_final_snapshot = True
            db_instance.id = self.configuration.db_rds_instance_id_template.format(counter=counter)
            self.aws_api.rds_client.dispose_db_instance(db_instance)

        db_cluster_parameter_group = RDSDBClusterParameterGroup({})
        db_cluster_parameter_group.region = self.region
        db_cluster_parameter_group.name = self.configuration.db_rds_cluster_parameter_group_name
        self.aws_api.rds_client.dispose_cluster_parameter_group(db_cluster_parameter_group)

        db_parameter_group = RDSDBParameterGroup({})
        db_parameter_group.region = self.region
        db_parameter_group.name = self.configuration.db_rds_instance_parameter_group_name
        self.aws_api.rds_client.dispose_parameter_group(db_cluster_parameter_group)

        subnet_group = RDSDBSubnetGroup({"name": self.configuration.db_rds_subnet_group_name})
        subnet_group.region = self.region
        self.aws_api.rds_client.dispose_db_subnet_group(subnet_group)
