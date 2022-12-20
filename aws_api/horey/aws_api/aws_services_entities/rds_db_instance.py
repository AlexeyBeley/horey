"""
Module to handle AWS RDS instances
"""
from enum import Enum

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class RDSDBInstance(AwsObject):
    """
    Class representing RDS DB instance
    """
    # pylint: disable = too-many-instance-attributes

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.endpoint = {}
        self.vpc_security_groups = []
        self.availability_zones = None
        self.kms_key_id = None
        self.deletion_protection = None
        self.deletion_protection = None
        self.master_user_password = None
        self.master_username = None
        self.db_name = None
        self.db_subnet_group_name = None
        self.db_parameter_group_name = None
        self.db_cluster_identifier = None
        self.db_instance_class = None
        self.engine_version = None
        self.preferred_maintenance_window = None
        self.storage_encrypted = None
        self.skip_final_snapshot = None
        self.copy_tags_to_snapshot = None
        self.db_instance_status = None
        self.engine = None
        self.arn = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "DBInstanceIdentifier": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "DBInstanceArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
            "DBInstanceClass": self.init_default_attr,
            "Engine": self.init_default_attr,
            "DBInstanceStatus": self.init_default_attr,
            "MasterUsername": self.init_default_attr,
            "Endpoint": self.init_default_attr,
            "AllocatedStorage": self.init_default_attr,
            "InstanceCreateTime": self.init_default_attr,
            "PreferredBackupWindow": self.init_default_attr,
            "BackupRetentionPeriod": self.init_default_attr,
            "DBSecurityGroups": self.init_default_attr,
            "VpcSecurityGroups": self.init_default_attr,
            "DBParameterGroups": self.init_default_attr,
            "AvailabilityZone": self.init_default_attr,
            "DBSubnetGroup": self.init_default_attr,
            "PreferredMaintenanceWindow": self.init_default_attr,
            "PendingModifiedValues": self.init_default_attr,
            "LatestRestorableTime": self.init_default_attr,
            "MultiAZ": self.init_default_attr,
            "EngineVersion": self.init_default_attr,
            "AutoMinorVersionUpgrade": self.init_default_attr,
            "ReadReplicaDBInstanceIdentifiers": self.init_default_attr,
            "LicenseModel": self.init_default_attr,
            "OptionGroupMemberships": self.init_default_attr,
            "PubliclyAccessible": self.init_default_attr,
            "StorageType": self.init_default_attr,
            "DbInstancePort": self.init_default_attr,
            "StorageEncrypted": self.init_default_attr,
            "KmsKeyId": self.init_default_attr,
            "DbiResourceId": self.init_default_attr,
            "CACertificateIdentifier": self.init_default_attr,
            "DomainMemberships": self.init_default_attr,
            "CopyTagsToSnapshot": self.init_default_attr,
            "MonitoringInterval": self.init_default_attr,
            "IAMDatabaseAuthenticationEnabled": self.init_default_attr,
            "PerformanceInsightsEnabled": self.init_default_attr,
            "DeletionProtection": self.init_default_attr,
            "EnhancedMonitoringResourceArn": self.init_default_attr,
            "MonitoringRoleArn": self.init_default_attr,
            "DBName": self.init_default_attr,
            "ReadReplicaSourceDBInstanceIdentifier": self.init_default_attr,
            "StatusInfos": self.init_default_attr,
            "SecondaryAvailabilityZone": self.init_default_attr,
            "DBClusterIdentifier": self.init_default_attr,
            "PromotionTier": self.init_default_attr,
            "AssociatedRoles": self.init_default_attr,
            "TagList": self.init_default_attr,
            "CustomerOwnedIpEnabled": self.init_default_attr,
            "PerformanceInsightsKMSKeyId": self.init_default_attr,
            "PerformanceInsightsRetentionPeriod": self.init_default_attr,
            "EnabledCloudwatchLogsExports": self.init_default_attr,
            "BackupTarget": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def _init_object_from_cache(self, dict_src):
        """
        Init the object from saved cache dict
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def get_dns_records(self):
        """
        Get self dns address
        :return: list of self dns records, [] else
        """
        # pylint: disable=E1136
        ret = [self.endpoint["Address"]] if self.endpoint["Address"] else []
        return ret

    def get_security_groups_endpoints(self):
        """
        Get sg ids, specified in this rds if there is "inactive" raises Exception

        :return:
        """
        ret = []
        for sg in self.vpc_security_groups:
            if sg["Status"] != "active":
                raise Exception("Unknown status")

            endpoint = {"sg_id": sg["VpcSecurityGroupId"],
                        "dns": self.endpoint["Address"],
                        "port": self.endpoint["Port"],
                        "description": f"rds: {self.name}"}

            ret.append(endpoint)

        return ret

    def generate_create_request(self):
        """
                response = client.create_db_cluster(

        )
        """
        request = {}
        if self.availability_zones:
            request["AvailabilityZones"] = self.availability_zones

        if self.db_subnet_group_name:
            request["DBSubnetGroupName"] = self.db_subnet_group_name

        if self.db_parameter_group_name:
            request["DBParameterGroupName"] = self.db_parameter_group_name

        request["DBInstanceIdentifier"] = self.id
        request["DBClusterIdentifier"] = self.db_cluster_identifier
        request["DBInstanceClass"] = self.db_instance_class

        if self.db_name is not None:
            request["DBName"] = self.db_name

        request["Engine"] = self.engine
        request["EngineVersion"] = self.engine_version

        if self.master_username is not None:
            request["MasterUsername"] = self.master_username

        if self.master_user_password is not None:
            request["MasterUserPassword"] = self.master_user_password

        request["PreferredMaintenanceWindow"] = self.preferred_maintenance_window
        request["StorageEncrypted"] = self.storage_encrypted

        if self.kms_key_id:
            request["KmsKeyId"] = self.kms_key_id

        if self.deletion_protection is not None:
            request["DeletionProtection"] = self.deletion_protection

        request["CopyTagsToSnapshot"] = self.copy_tags_to_snapshot

        request["Tags"] = self.tags

        return request

    def generate_dispose_request(self):
        """
        Standard.

        :return:
        """

        request = {"DBInstanceIdentifier": self.id, "SkipFinalSnapshot": self.skip_final_snapshot}
        if self.skip_final_snapshot:
            request["DeleteAutomatedBackups"] = True
        return request

    @property
    def region(self):
        """
        Standard.

        :return:
        """

        if self._region is not None:
            return self._region

        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        """
        Standard.

        :param value:
        :return:
        """

        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value

    def update_from_raw_response(self, dict_src):
        """
        Standard.

        :param dict_src:
        :return:
        """

        init_options = {
            "DBInstanceIdentifier": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "DBInstanceClass": self.init_default_attr,
            "Engine": self.init_default_attr,
            "DBInstanceStatus": self.init_default_attr,
            "MasterUsername": self.init_default_attr,
            "Endpoint": self.init_default_attr,
            "AllocatedStorage": self.init_default_attr,
            "InstanceCreateTime": self.init_default_attr,
            "PreferredBackupWindow": self.init_default_attr,
            "BackupRetentionPeriod": self.init_default_attr,
            "DBSecurityGroups": self.init_default_attr,
            "VpcSecurityGroups": self.init_default_attr,
            "DBParameterGroups": self.init_default_attr,
            "AvailabilityZone": self.init_default_attr,
            "DBSubnetGroup": self.init_default_attr,
            "PreferredMaintenanceWindow": self.init_default_attr,
            "PendingModifiedValues": self.init_default_attr,
            "LatestRestorableTime": self.init_default_attr,
            "MultiAZ": self.init_default_attr,
            "EngineVersion": self.init_default_attr,
            "AutoMinorVersionUpgrade": self.init_default_attr,
            "ReadReplicaDBInstanceIdentifiers": self.init_default_attr,
            "LicenseModel": self.init_default_attr,
            "OptionGroupMemberships": self.init_default_attr,
            "PubliclyAccessible": self.init_default_attr,
            "StorageType": self.init_default_attr,
            "DbInstancePort": self.init_default_attr,
            "StorageEncrypted": self.init_default_attr,
            "KmsKeyId": self.init_default_attr,
            "DbiResourceId": self.init_default_attr,
            "CACertificateIdentifier": self.init_default_attr,
            "DomainMemberships": self.init_default_attr,
            "CopyTagsToSnapshot": self.init_default_attr,
            "MonitoringInterval": self.init_default_attr,
            "DBInstanceArn": self.init_default_attr,
            "IAMDatabaseAuthenticationEnabled": self.init_default_attr,
            "PerformanceInsightsEnabled": self.init_default_attr,
            "DeletionProtection": self.init_default_attr,
            "EnhancedMonitoringResourceArn": self.init_default_attr,
            "MonitoringRoleArn": self.init_default_attr,
            "DBName": self.init_default_attr,
            "ReadReplicaSourceDBInstanceIdentifier": self.init_default_attr,
            "StatusInfos": self.init_default_attr,
            "SecondaryAvailabilityZone": self.init_default_attr,
            "DBClusterIdentifier": self.init_default_attr,
            "PromotionTier": self.init_default_attr,
            "AssociatedRoles": self.init_default_attr,
            "TagList": self.init_default_attr,
            "CustomerOwnedIpEnabled": self.init_default_attr,
            "PerformanceInsightsKMSKeyId": self.init_default_attr,
            "PerformanceInsightsRetentionPeriod": self.init_default_attr,
            "EnabledCloudwatchLogsExports": self.init_default_attr,
            "BackupTarget": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def get_status(self):
        """
        Instance status.

        :return:
        """

        return {
            enum_value.value: enum_value
            for _, enum_value in self.Status.__members__.items()
        }[self.db_instance_status]

    class Status(Enum):
        """
        Instance status.

        """

        AVAILABLE = "available"
        CREATING = "creating"
        DELETING = "deleting"
        MODIFYING = "modifying"
        FAILED = "failed"
        STARTING = "starting"
        STOPPED = "stopped"
        STOPPING = "stopping"
        CONFIGURING_ENHANCED_MONITORING = "configuring-enhanced-monitoring"
        CONFIGURING_LOG_EXPORTS = "configuring-log-exports"
