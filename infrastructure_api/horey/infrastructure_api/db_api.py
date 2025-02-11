"""
Standard Load balancing maintainer.

"""

from horey.h_logger import get_logger
from horey.aws_api.aws_services_entities.route53_hosted_zone import HostedZone
from horey.aws_api.aws_services_entities.rds_db_cluster import RDSDBCluster
from horey.aws_api.aws_services_entities.rds_db_instance import RDSDBInstance
from horey.aws_api.aws_services_entities.rds_db_cluster_parameter_group import RDSDBClusterParameterGroup
from horey.aws_api.aws_services_entities.rds_db_parameter_group import RDSDBParameterGroup
from horey.aws_api.aws_services_entities.rds_db_subnet_group import RDSDBSubnetGroup


logger = get_logger()


class DBAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api
        self._max_version_raw = None

    def provision(self):
        """
        Provision ECS infrastructure.

        :return:
        """

        self.environment_api.aws_api.rds_client.clear_cache(None, all_cache=True)
        self.provision_serverless_cluster_parameter_group()
        self.provision_db_instance_parameter_group()
        self.provision_rds_subnet_group()

        self.provision_cluster_serverless()
        self.provision_rds_db_instances()
        self.provision_domain_names()        
        return True

    def get_hosted_zone(self, hz_name):
        """
        Standard.

        :param hz_name:
        :return:
        """

        hosted_zone = HostedZone({})
        hosted_zone.name = hz_name
        if not self.environment_api.aws_api.route53_client.update_hosted_zone_information(hosted_zone):
            raise RuntimeError(f"Was not able to find hosted zone: '{hz_name}'")

        return hosted_zone

    def update(self):
        """

        :return:
        """

        breakpoint()
    
    @property
    def max_version_raw(self):
        """
        The maximum version available in RDS

        :return:
        """

        if self._max_version_raw is None:
            self._max_version_raw = self.environment_api.aws_api.rds_client.get_engine_max_version(self.environment_api.region,
                                                                                   self.configuration.engine_type,
                                                                                   raw=True)
        return self._max_version_raw

    def provision_serverless_cluster_parameter_group(self):
        """
        Parameters used by the serverless cluster.

        :return:
        """
        breakpoint()
        db_cluster_parameter_group = RDSDBClusterParameterGroup({})
        db_cluster_parameter_group.region = self.environment_api.region
        db_cluster_parameter_group.name = self.configuration.cluster_parameter_group_name
        db_cluster_parameter_group.db_parameter_group_family = self.max_version_raw["DBParameterGroupFamily"]
        db_cluster_parameter_group.description = db_cluster_parameter_group.name
        db_cluster_parameter_group.tags = self.environment_api.configuration.tags
        db_cluster_parameter_group.tags.append({
            "Key": "name",
            "Value": db_cluster_parameter_group.name
        })

        # todo: binlog_format db_cluster_parameter_group.parameters = [{}]
        """
        response = rds.modify_db_cluster_parameter_group(
            DBClusterParameterGroupName=get_parameter_group_name(db_cluster_identifier), #Dynamically get the parameter group
            ParameterGroupFamily='mysql8.0',  # Important: Specify the correct family
            Parameters=[
                {
                    'ParameterName': 'binlog_format',
                    'ParameterValue': "ROW",
                    'ApplyMethod': 'immediate'
                },
            ],
            ApplyImmediately=True #Applies changes immediately. If false, the changes will take effect after a reboot.
        )
        print(f"Successfully set binlog_format to {binlog_format} for cluster {db_cluster_identifier}")
        #print(response) #Uncomment for debugging
        """
        self.environment_api.aws_api.provision_db_cluster_parameter_group(db_cluster_parameter_group)
        return True

    def provision_rds_subnet_group(self):
        """
        Subnets used by the cluster.

        :return:
        """
        subnet_group = RDSDBSubnetGroup({})
        subnet_group.region = self.environment_api.region
        subnet_group.name = self.configuration.subnet_group_name
        subnet_group.db_subnet_group_description = self.configuration.subnet_group_name
        subnet_group.subnet_ids = [subnet.id for subnet in self.select_subnets("private")]
        subnet_group.tags = self.environment_api.configuration.tags 
        subnet_group.tags.append({
            "Key": "name",
            "Value": subnet_group.name
        }
        )
        self.environment_api.aws_api.provision_db_subnet_group(subnet_group)
        return True

    def provision_cluster_serverless(self):
        """
        Serverless class

        :return:
        """

        db_postgres_test_results_security_group = self.environment_api.aws_api.get_security_group_by_vpc_and_name(self.vpc,
                                                                                                  self.configuration.db_postgres_test_results_security_group_name)

        cluster = RDSDBCluster({})
        cluster.region = self.environment_api.region
        cluster.db_subnet_group_name = self.configuration.subnet_group_name
        cluster.db_cluster_parameter_group_name = self.configuration.cluster_parameter_group_name_serverless
        cluster.backup_retention_period = self.configuration.backup_retention_days
        cluster.database_name = self.configuration.db_postgres_test_results_database_name
        cluster.id = self.configuration.postgres_cluster_identifier
        cluster.vpc_security_group_ids = [db_postgres_test_results_security_group.id]
        engine_version_raw = self.environment_api.aws_api.rds_client.get_engine_version(self.environment_api.region, self.configuration.engine_type,
                                                                        self.max_version_raw["EngineVersion"])
        cluster.engine = engine_version_raw["Engine"]
        cluster.engine_version = engine_version_raw["EngineVersion"]

        cluster.port = 5432

        cluster.master_username = self.secrets.get_secret(
            self.configuration.db_postgres_test_results_master_username_secret_name)
        cluster.manage_master_user_password = False
        cluster.master_user_password = self.secrets.get_secret(
            self.configuration.db_postgres_test_results_master_password_secret_name)
        cluster.preferred_backup_window = "09:23-09:53"
        cluster.preferred_maintenance_window = "sun:03:30-sun:04:00"
        cluster.storage_encrypted = True
        cluster.engine_mode = "provisioned"

        cluster.deletion_protection = self.configuration.deletion_protection
        cluster.copy_tags_to_snapshot = True
        cluster.enable_cloudwatch_logs_exports = [
            "postgresql",
        ]
        cluster.tags = self.environment_api.configuration.tags  
        cluster.tags.append({
            "Key": "name",
            "Value": cluster.id
        }
        )
        cluster.serverless_v2_scaling_configuration = self.configuration.serverless_v2_scaling_configuration
        cluster.auto_minor_version_upgrade = True

        self.environment_api.aws_api.provision_rds_db_cluster(cluster)
        return True

    def provision_db_instance_parameter_group(self):
        """
        Database param group.

        :return:
        """

        db_parameter_group = RDSDBParameterGroup({})
        db_parameter_group.region = self.environment_api.region
        db_parameter_group.name = self.configuration.instance_parameter_group_name_serverless
        db_parameter_group.db_parameter_group_family = self.max_version_raw["DBParameterGroupFamily"]
        db_parameter_group.description = db_parameter_group.name
        db_parameter_group.tags = self.environment_api.configuration.tags  
        db_parameter_group.tags.append({
            "Key": "name",
            "Value": db_parameter_group.name
        }
        )

        self.environment_api.aws_api.provision_db_parameter_group(db_parameter_group)
        return True

    def provision_rds_db_instances(self):
        """
        Provision all the instances.

        :return:
        """

        logger.info("Starting provisioning fb instances")

        for counter in range(self.configuration.db_instance_count):
            db_instance = RDSDBInstance({})
            db_instance.region = self.environment_api.region

            db_instance.id = self.configuration.instance_name_format.format(counter=counter)

            db_instance.db_cluster_identifier = self.configuration.postgres_cluster_identifier
            db_instance.db_subnet_group_name = self.configuration.subnet_group_name
            db_instance.db_parameter_group_name = self.configuration.instance_parameter_group_name_serverless
            engine_version_raw = self.environment_api.aws_api.rds_client.get_engine_version(self.environment_api.region, self.configuration.engine_type,
                                                                            self.max_version_raw["EngineVersion"])
            db_instance.engine = engine_version_raw["Engine"]
            db_instance.engine_version = engine_version_raw["EngineVersion"]

            db_instance.preferred_maintenance_window = "sun:03:30-sun:04:00"
            db_instance.storage_encrypted = True

            db_instance.copy_tags_to_snapshot = True
            db_instance.db_instance_class = self.configuration.db_cluster_instance_class

            db_instance.tags = self.environment_api.configuration.tags
            db_instance.tags.append({
                "Key": "name",
                "Value": db_instance.id
            }
            )
            self.environment_api.aws_api.provision_db_instance(db_instance)
            logger.info(f"Provisioned DB instance: {counter}")
        return True
