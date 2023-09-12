"""
Module to handle AWS RDS instances
"""
from enum import Enum

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region

# pylint: disable=too-many-instance-attributes


class RDSDBCluster(AwsObject):
    """
    Class representing RDS DB instance
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None
        self.availability_zones = None
        self.db_subnet_group_name = None
        self.db_cluster_parameter_group_name = None
        self.kms_key_id = None
        self.cluster_create_time = None

        self.backup_retention_period = None
        self.database_name = None
        self.id = None
        self.vpc_security_group_ids = None
        self.engine = None
        self.engine_version = None
        self.port = None

        self.master_username = None
        self.master_user_password = None
        self.preferred_backup_window = None
        self.preferred_maintenance_window = None
        self.storage_encrypted = None
        self.enabled_cloudwatch_logs_exports = None
        self.kms_key_id = None
        self.engine_mode = None
        self.deletion_protection = None
        self.copy_tags_to_snapshot = None
        self.arn = None
        self.status = None
        self.skip_final_snapshot = False
        self.default_engine_version = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        self.update_from_raw_response(dict_src)

    def _init_object_from_cache(self, dict_src):
        """
        Init the object from saved cache dict
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def update_from_raw_response(self, dict_src):
        """
        Standard

        @param dict_src:
        @return:
        """
        init_options = {
            "DBClusterIdentifier": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "DBClusterArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
            "AllocatedStorage": self.init_default_attr,
            "AvailabilityZones": self.init_default_attr,
            "BackupRetentionPeriod": self.init_default_attr,
            "DatabaseName": self.init_default_attr,
            "DBClusterParameterGroup": self.init_default_attr,
            "DBSubnetGroup": self.init_default_attr,
            "Status": self.init_default_attr,
            "EarliestRestorableTime": self.init_default_attr,
            "Endpoint": self.init_default_attr,
            "ReaderEndpoint": self.init_default_attr,
            "MultiAZ": self.init_default_attr,
            "Engine": self.init_default_attr,
            "EngineVersion": self.init_default_attr,
            "LatestRestorableTime": self.init_default_attr,
            "Port": self.init_default_attr,
            "MasterUsername": self.init_default_attr,
            "PreferredBackupWindow": self.init_default_attr,
            "PreferredMaintenanceWindow": self.init_default_attr,
            "ReadReplicaIdentifiers": self.init_default_attr,
            "DBClusterMembers": self.init_default_attr,
            "VpcSecurityGroups": self.init_default_attr,
            "HostedZoneId": self.init_default_attr,
            "StorageEncrypted": self.init_default_attr,
            "KmsKeyId": self.init_default_attr,
            "DbClusterResourceId": self.init_default_attr,
            "AssociatedRoles": self.init_default_attr,
            "IAMDatabaseAuthenticationEnabled": self.init_default_attr,
            "ClusterCreateTime": self.init_default_attr,
            "EnabledCloudwatchLogsExports": self.init_default_attr,
            "EngineMode": self.init_default_attr,
            "DeletionProtection": self.init_default_attr,
            "HttpEndpointEnabled": self.init_default_attr,
            "ActivityStreamStatus": self.init_default_attr,
            "CopyTagsToSnapshot": self.init_default_attr,
            "CrossAccountClone": self.init_default_attr,
            "DomainMemberships": self.init_default_attr,
            "TagList": self.init_default_attr,
            "PendingModifiedValues": self.init_default_attr,
            "AutoMinorVersionUpgrade": self.init_default_attr,
            "NetworkType": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard

        """
        request = {}
        if self.availability_zones:
            request["AvailabilityZones"] = self.availability_zones

        if self.db_subnet_group_name:
            request["DBSubnetGroupName"] = self.db_subnet_group_name

        if self.db_cluster_parameter_group_name:
            request[
                "DBClusterParameterGroupName"
            ] = self.db_cluster_parameter_group_name

        request["BackupRetentionPeriod"] = self.backup_retention_period
        request["DatabaseName"] = self.database_name
        request["DBClusterIdentifier"] = self.id
        request["VpcSecurityGroupIds"] = self.vpc_security_group_ids
        request["Engine"] = self.engine
        request["EngineVersion"] = self.engine_version
        request["Port"] = self.port

        request["MasterUsername"] = self.master_username
        request["MasterUserPassword"] = self.master_user_password
        request["PreferredBackupWindow"] = self.preferred_backup_window
        request["PreferredMaintenanceWindow"] = self.preferred_maintenance_window
        request["StorageEncrypted"] = self.storage_encrypted

        request["EnableCloudwatchLogsExports"] = self.enabled_cloudwatch_logs_exports

        if self.kms_key_id:
            request["KmsKeyId"] = self.kms_key_id

        request["EngineMode"] = self.engine_mode

        request["DeletionProtection"] = self.deletion_protection
        request["CopyTagsToSnapshot"] = self.copy_tags_to_snapshot

        request["Tags"] = self.tags

        return request

    def generate_dispose_request(self):
        """
        Standard

        @return:
        """
        request = {
            "DBClusterIdentifier": self.id,
            "SkipFinalSnapshot": self.skip_final_snapshot,
        }
        return request

    def generate_modify_request(self):
        """
        Standard

        @return:
        """
        request = {
            "DBClusterIdentifier": self.id,
            "MasterUserPassword": self.master_user_password,
            "ApplyImmediately": True,
        }
        return request

    def generate_restore_db_cluster_from_snapshot_request(self, snapshot_id):
        """
        Standard

        @param snapshot_id:
        @return:
        """
        request = {}
        if self.availability_zones:
            request["AvailabilityZones"] = self.availability_zones

        if self.db_subnet_group_name:
            request["DBSubnetGroupName"] = self.db_subnet_group_name

        if self.db_cluster_parameter_group_name:
            request[
                "DBClusterParameterGroupName"
            ] = self.db_cluster_parameter_group_name

        request["SnapshotIdentifier"] = snapshot_id
        request["DBClusterIdentifier"] = self.id
        request["VpcSecurityGroupIds"] = self.vpc_security_group_ids
        request["Engine"] = self.engine
        request["EngineVersion"] = self.engine_version
        request["Port"] = self.port

        request["EnableCloudwatchLogsExports"] = self.enabled_cloudwatch_logs_exports

        if self.kms_key_id:
            request["KmsKeyId"] = self.kms_key_id

        request["EngineMode"] = self.engine_mode

        request["DeletionProtection"] = self.deletion_protection
        request["CopyTagsToSnapshot"] = False

        request["Tags"] = self.tags

        return request

    @property
    def region(self):
        """
        Standard

        @return:
        """
        if self._region is not None:
            return self._region

        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        """
        Standard

        @param value:
        @return:
        """
        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value

    def get_status(self):
        """
        Used by waiter loop.

        @return:
        """
        return {
            enum_value.value: enum_value
            for _, enum_value in self.Status.__members__.items()
        }[self.status]

    class Status(Enum):
        """
        CONFIGURING_ENHANCED_MONITORING = "configuring-enhanced-monitoring"
        CONFIGURING_IA"configuring-iam-database-auth"
        BACKING_UP = "backing-up"
        "configuring-log-exports"
        "converting-to-vpc"
        "inaccessible-encryption-credentials"
        "incompatible-network"
        "incompatible-option-group"
        "incompatible-parameters"
        "incompatible-restore"
        "insufficient-capacity"
        "maintenance"
        "moving-to-vpc"
        "rebooting"
        "resetting-master-credentials"
        "renaming"
        "restore-error"
        "storage-full"
        "storage-optimization"
        "upgrading"
        """

        AVAILABLE = "available"
        CREATING = "creating"
        DELETING = "deleting"
        MODIFYING = "modifying"
        FAILED = "failed"
        STARTING = "starting"
        STOPPED = "stopped"
        STOPPING = "stopping"
        RESETTING_MASTER_CREDENTIALS = "resetting-master-credentials"
