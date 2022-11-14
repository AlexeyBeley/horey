"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class ElasticacheCluster(AwsObject):
    """
    Elasticache Cluster class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.instances = []

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

    def update_value_from_raw_response(self, raw_value):
        pdb.set_trace()

    def generate_create_request(self):
        request = dict()

        request["CacheClusterId"] = self.id
        request["ReplicationGroupId"] = self.replication_group_id
        request["AZMode"] = self.az_mode
        request["PreferredAvailabilityZones"] = self.preferred_availability_zones
        request["NumCacheNodes"] = self.num_cache_nodes
        request["CacheNodeType"] = self.cache_node_type
        request["Engine"] = self.engine
        request["EngineVersion"] = self.engine_version
        request["Tags"] = self.tags
        request["SecurityGroupIds"] = self.security_group_ids
        request["CacheParameterGroupName"] = self.cache_parameter_group_name
        request["CacheSubnetGroupName"] = self.cache_subnet_group_name

        request["PreferredMaintenanceWindow"] = self.preferred_maintenance_window
        request["AutoMinorVersionUpgrade"] = self.auto_minor_version_upgrade
        request["SnapshotRetentionLimit"] = self.snapshot_retention_limit
        request["SnapshotWindow"] = self.snapshot_window

        return request
