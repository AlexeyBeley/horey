"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class ElasticacheReplicationGroup(AwsObject):
    """
    Elasticache Cluster class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.security_group_ids = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "ARN": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "LogDeliveryConfigurations": self.init_default_attr,
            "ReplicationGroupId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "Description": self.init_default_attr,
            "GlobalReplicationGroupInfo": self.init_default_attr,
            "Status": self.init_default_attr,
            "PendingModifiedValues": self.init_default_attr,
            "MemberClusters": self.init_default_attr,
            "NodeGroups": self.init_default_attr,
            "SnapshottingClusterId": self.init_default_attr,
            "AutomaticFailover": self.init_default_attr,
            "MultiAZ": self.init_default_attr,
            "SnapshotRetentionLimit": self.init_default_attr,
            "SnapshotWindow": self.init_default_attr,
            "ClusterEnabled": self.init_default_attr,
            "CacheNodeType": self.init_default_attr,
            "AuthTokenEnabled": self.init_default_attr,
            "TransitEncryptionEnabled": self.init_default_attr,
            "AtRestEncryptionEnabled": self.init_default_attr,
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

        request["ReplicationGroupId"] = self.id
        request["ReplicationGroupDescription"] = self.description

        request["PreferredCacheClusterAZs"] = self.preferred_cache_cluster_azs
        request["CacheNodeType"] = self.cache_node_type
        request["Engine"] = self.engine
        request["EngineVersion"] = self.engine_version
        request["Tags"] = self.tags

        if self.security_group_ids is not None:
            request["SecurityGroupIds"] = self.security_group_ids

        request["CacheParameterGroupName"] = self.cache_parameter_group_name
        request["CacheSubnetGroupName"] = self.cache_subnet_group_name

        request["PreferredMaintenanceWindow"] = self.preferred_maintenance_window
        request["AutoMinorVersionUpgrade"] = self.auto_minor_version_upgrade
        request["SnapshotRetentionLimit"] = self.snapshot_retention_limit
        request["SnapshotWindow"] = self.snapshot_window

        request["NumCacheClusters"] = self.num_cache_clusters
        return request

    def update_from_raw_response(self, dict_src):
        init_options = {
            "ARN": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "LogDeliveryConfigurations": self.init_default_attr,
            "ReplicationGroupId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "Description": self.init_default_attr,
            "GlobalReplicationGroupInfo": self.init_default_attr,
            "Status": self.init_default_attr,
            "PendingModifiedValues": self.init_default_attr,
            "MemberClusters": self.init_default_attr,
            "NodeGroups": self.init_default_attr,
            "SnapshottingClusterId": self.init_default_attr,
            "AutomaticFailover": self.init_default_attr,
            "MultiAZ": self.init_default_attr,
            "SnapshotRetentionLimit": self.init_default_attr,
            "SnapshotWindow": self.init_default_attr,
            "ClusterEnabled": self.init_default_attr,
            "CacheNodeType": self.init_default_attr,
            "AuthTokenEnabled": self.init_default_attr,
            "TransitEncryptionEnabled": self.init_default_attr,
            "AtRestEncryptionEnabled": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def get_primary_endpoint_address(self):
        if len(self.node_groups) != 1:
            raise NotImplementedError(f"len(self.node_groups) != 1: {self.node_groups}")
        return self.node_groups[0]["PrimaryEndpoint"]["Address"]

    def get_primary_endpoint_port(self):
        pdb.set_trace()
