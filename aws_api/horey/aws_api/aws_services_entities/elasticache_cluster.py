"""
AWS object representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


# pylint: disable= too-many-instance-attributes
class ElasticacheCluster(AwsObject):
    """
    Elasticache Cluster class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.replication_group_id = None
        self.az_mode = None
        self.preferred_availability_zones = None
        self.num_cache_nodes = None
        self.cache_node_type = None
        self.engine = None
        self.engine_version = None
        self.tags = None
        self.security_group_ids = None
        self.cache_parameter_group_name = None
        self.cache_subnet_group_name = None
        self.preferred_maintenance_window = None
        self.auto_minor_version_upgrade = None
        self.snapshot_retention_limit = None
        self.snapshot_window = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "ARN": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "CacheClusterId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "ClientDownloadLandingPage": self.init_default_attr,
            "CacheNodeType": self.init_default_attr,
            "Engine": self.init_default_attr,
            "EngineVersion": self.init_default_attr,
            "CacheClusterStatus": self.init_default_attr,
            "NumCacheNodes": self.init_default_attr,
            "PreferredAvailabilityZone": self.init_default_attr,
            "CacheClusterCreateTime": self.init_default_attr,
            "PreferredMaintenanceWindow": self.init_default_attr,
            "PendingModifiedValues": self.init_default_attr,
            "CacheSecurityGroups": self.init_default_attr,
            "CacheParameterGroup": self.init_default_attr,
            "CacheSubnetGroupName": self.init_default_attr,
            "AutoMinorVersionUpgrade": self.init_default_attr,
            "SecurityGroups": self.init_default_attr,
            "ReplicationGroupId": self.init_default_attr,
            "SnapshotRetentionLimit": self.init_default_attr,
            "SnapshotWindow": self.init_default_attr,
            "AuthTokenEnabled": self.init_default_attr,
            "TransitEncryptionEnabled": self.init_default_attr,
            "AtRestEncryptionEnabled": self.init_default_attr,
            "ReplicationGroupLogDeliveryEnabled": self.init_default_attr,
            "LogDeliveryConfigurations": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def _init_object_from_cache(self, dict_src):
        """
        Init from cache
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def generate_create_request(self):
        """
        Standard
        :return:
        """
        request = {"CacheClusterId": self.id,
                   "ReplicationGroupId": self.replication_group_id,
                   "AZMode": self.az_mode,
                   "PreferredAvailabilityZones": self.preferred_availability_zones,
                   "NumCacheNodes": self.num_cache_nodes,
                   "CacheNodeType": self.cache_node_type,
                   "Engine": self.engine,
                   "EngineVersion": self.engine_version,
                   "Tags": self.tags,
                   "SecurityGroupIds": self.security_group_ids,
                   "CacheParameterGroupName": self.cache_parameter_group_name,
                   "CacheSubnetGroupName": self.cache_subnet_group_name,
                   "PreferredMaintenanceWindow": self.preferred_maintenance_window,
                   "AutoMinorVersionUpgrade": self.auto_minor_version_upgrade,
                   "SnapshotRetentionLimit": self.snapshot_retention_limit,
                   "SnapshotWindow": self.snapshot_window}

        return request
