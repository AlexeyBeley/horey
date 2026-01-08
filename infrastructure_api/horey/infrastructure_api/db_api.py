"""
Standard Load balancing maintainer.

"""
from horey.aws_api.aws_services_entities.glue_database import GlueDatabase
from horey.aws_api.aws_services_entities.glue_table import GlueTable
from horey.h_logger import get_logger
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
        self.dns_api = None

    def provision(self):
        """
        Provision ECS infrastructure.

        :return:
        """

        # todo: cleanup report delete unused parameter groups.

        self.environment_api.aws_api.rds_client.clear_cache(None, all_cache=True)
        self.provision_serverless_cluster_parameter_group()
        self.provision_db_instance_parameter_group()
        self.provision_rds_subnet_group()

        self.provision_cluster_serverless()
        self.provision_rds_db_instances()
        self.provision_domain_names()
        return True

    def set_api(self, dns_api=None):
        """
        Set APIs

        :param dns_api:
        :return:
        """

        if dns_api:
            if not dns_api.configuration.hosted_zone_name:
                raise NotImplementedError("Must have hosted_zone_name set in the dns api")
            self.dns_api = dns_api

    @property
    def max_version_raw(self):
        """
        The maximum version available in RDS

        :return:
        """
        if self._max_version_raw is None:
            self._max_version_raw = self.environment_api.aws_api.rds_client.get_engine_max_version(
                self.environment_api.region,
                self.configuration.engine_type,
                raw=True)
        return self._max_version_raw

    def provision_serverless_cluster_parameter_group(self):
        """
        Parameters used by the serverless cluster.

        :return:
        """

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
        db_cluster_parameter_group.parameters = [{"ParameterName": "binlog_format",
                                                  "ParameterValue": "ROW",
                                                  "Description": "Binary logging format for replication",
                                                  "Source": "user", 
                                                  "ApplyType": "static", 
                                                  "DataType": "string",
                                                  "AllowedValues": "ROW,STATEMENT,MIXED,OFF", 
                                                  "IsModifiable": True,
                                                  "ApplyMethod": "pending-reboot",
                                                  "SupportedEngineModes": ["provisioned"]}]

        self.environment_api.aws_api.provision_db_cluster_parameter_group(db_cluster_parameter_group)
        return True

    def provision_db_instance_parameter_group(self):
        """
        Database param group.

        :return:
        """

        db_parameter_group = RDSDBParameterGroup({})
        db_parameter_group.region = self.environment_api.region
        db_parameter_group.name = self.configuration.instance_parameter_group_name
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

    def provision_rds_subnet_group(self):
        """
        Subnets used by the cluster.

        :return:
        """
        subnet_group = RDSDBSubnetGroup({})
        subnet_group.region = self.environment_api.region
        subnet_group.name = self.configuration.subnet_group_name
        subnet_group.db_subnet_group_description = self.configuration.subnet_group_name
        subnet_group.subnet_ids = [subnet.id for subnet in self.environment_api.private_subnets]
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
        security_groups = self.environment_api.get_security_groups(self.configuration.security_group_names)

        cluster = RDSDBCluster({})
        cluster.region = self.environment_api.region
        cluster.db_subnet_group_name = self.configuration.subnet_group_name
        cluster.db_cluster_parameter_group_name = self.configuration.cluster_parameter_group_name
        cluster.backup_retention_period = self.configuration.backup_retention_days
        cluster.database_name = self.configuration.database_name
        cluster.id = self.configuration.cluster_name
        cluster.vpc_security_group_ids = [security_group.id for security_group in security_groups]
        engine_version_raw = self.environment_api.aws_api.rds_client.get_engine_version(self.environment_api.region,
                                                                                        self.configuration.engine_type,
                                                                                        self.max_version_raw[
                                                                                            "EngineVersion"])
        cluster.engine = engine_version_raw["Engine"]
        cluster.engine_version = engine_version_raw["EngineVersion"]

        if "postgres" in cluster.engine.lower():
            cluster.port = 5432

            cluster.enable_cloudwatch_logs_exports = [
                "postgresql",
            ]
        elif "mysql" in cluster.engine.lower():
            cluster.port = 3306
            cluster.enable_cloudwatch_logs_exports = ["audit", "error", "general", "instance", "slowquery"]
        else:
            raise RuntimeError(f"Not implemented: {cluster.engine}")

        cluster.master_username = self.configuration.master_username
        cluster.manage_master_user_password = True
        # cluster.master_user_password = self.get_secret(
        #     self.configuration.password_secret_name)
        cluster.preferred_backup_window = "07:30-08:00"
        cluster.preferred_maintenance_window = "mon:06:00-mon:07:00"
        cluster.storage_encrypted = True
        cluster.engine_mode = "provisioned"

        cluster.deletion_protection = self.configuration.deletion_protection
        cluster.copy_tags_to_snapshot = True

        cluster.tags = self.environment_api.configuration.tags
        cluster.tags.append({
            "Key": "name",
            "Value": cluster.id
        }
        )
        cluster.serverless_v2_scaling_configuration = self.configuration.serverless_v2_scaling_configuration
        cluster.auto_minor_version_upgrade = True

        self.environment_api.aws_api.provision_rds_db_cluster(cluster)
        return cluster

    def provision_rds_db_instances(self):
        """
        Provision all the instances.

        :return:
        """

        logger.info("Starting provisioning fb instances")

        for counter in range(self.configuration.db_instance_count):
            db_instance = RDSDBInstance({})
            db_instance.region = self.environment_api.region

            db_instance.id = self.configuration.instance_name_format.format(id=counter)

            db_instance.db_cluster_identifier = self.configuration.cluster_name
            db_instance.db_subnet_group_name = self.configuration.subnet_group_name
            db_instance.db_parameter_group_name = self.configuration.instance_parameter_group_name
            engine_version_raw = self.environment_api.aws_api.rds_client.get_engine_version(self.environment_api.region,
                                                                                            self.configuration.engine_type,
                                                                                            self.max_version_raw[
                                                                                                "EngineVersion"])
            db_instance.engine = engine_version_raw["Engine"]
            db_instance.engine_version = engine_version_raw["EngineVersion"]

            db_instance.preferred_maintenance_window = "mon:06:00-mon:07:00"
            db_instance.storage_encrypted = True

            db_instance.copy_tags_to_snapshot = True
            db_instance.db_instance_class = self.configuration.cluster_instance_class

            db_instance.tags = self.environment_api.configuration.tags
            db_instance.tags.append({
                "Key": "name",
                "Value": db_instance.id
            }
            )
            self.environment_api.aws_api.provision_db_instance(db_instance)
            logger.info(f"Provisioned DB instance: {counter}")
        return True

    def get_cluster(self):
        """
        Get the cluster object from API.

        :return:
        """

        cluster = RDSDBCluster({"DBClusterIdentifier": self.configuration.cluster_name})
        cluster.region = self.environment_api.region
        if not self.environment_api.aws_api.rds_client.update_cluster_information(cluster):
            raise ValueError(f"Was not able to find cluster {cluster.id} in region {cluster.region.region_mark}")
        return cluster

    @property
    def reader_dns_address(self):
        """
        DNS address to be used to access Readers

        :return:
        """

        return f"{self.configuration.cluster_name}-reader.{self.dns_api.configuration.hosted_zone_name}"

    @property
    def writer_dns_address(self):
        """
        DNS address to be used to access Writers

        :return:
        """

        return f"{self.configuration.cluster_name}-writer.{self.dns_api.configuration.hosted_zone_name}"

    def provision_domain_names(self):
        """
        Provision cluster domain names

        :return:
        """

        if self.dns_api is None:
            return True

        cluster = self.get_cluster()
        self.dns_api.configuration.dns_target = cluster.reader_endpoint
        self.dns_api.configuration.dns_address = self.reader_dns_address
        self.dns_api.provision()

        self.dns_api.configuration.dns_target = cluster.endpoint
        self.dns_api.configuration.dns_address = self.writer_dns_address
        return self.dns_api.provision()

    def tags_dict(self):
        """
        Get tags dict.

        :return:
        """

        return {tag["Key"]: tag["Value"] for tag in self.environment_api.configuration.tags}


    def provision_glue_database(self, database_name: str) -> GlueDatabase:
        """
        Create glue database.
        :return:
        """

        database = GlueDatabase({})
        database.region = self.environment_api.region
        database.name = database_name
        database.tags = self.tags_dict()
        database.tags["Name"] = database_name

        self.environment_api.aws_api.glue_client.provision_database(database)
        return database

    def provision_glue_table(self, database_name:str, table_name: str, storage_descriptor, partition_keys)-> GlueTable:
        """
        Provision table

        :return:
        """

        table = GlueTable({})
        table.region = self.environment_api.region
        table.database_name = database_name
        table.name = table_name
        table.description = database_name
        table.retention = 0
        table.tags = self.tags_dict()
        table.tags["Name"] = table.name
        table.storage_descriptor = storage_descriptor
        table.parameters = {
            "EXTERNAL": "TRUE",
            "has_encrypted_data": "true",
            "transient_lastDdlTime": "1633420967"
        }
        table.partition_keys = partition_keys
        self.environment_api.aws_api.glue_client.provision_table(table)
        return table

    def dispose_glue_database(self, database_name: str) -> GlueDatabase:
        """
        Delete glue database if exists
        :return:
        """

        database = GlueDatabase({})
        database.region = self.environment_api.region
        database.name = database_name

        self.environment_api.aws_api.glue_client.dispose_database(database)
        return database

    def dispose_glue_table(self, database_name:str, table_name: str):
        """
        Provision table

        :return:
        """

        table = GlueTable({})
        table.region = self.environment_api.region
        table.database_name = database_name
        table.name = table_name
        self.environment_api.aws_api.glue_client.dispose_glue_table(table)
        return table
