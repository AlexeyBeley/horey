"""
AWS object representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


# pylint: disable= too-many-instance-attributes
class ElasticacheServerlessCache(AwsObject):
    """
    Elasticache Cluster class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.replication_group_id = None

        self.request_key_to_attribute_mapping = {"ARN": "arn", "ServerlessCacheName": "name"}

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        self.update_from_raw_response(dict_src)

    def update_from_raw_response(self, dict_src):
        """
        From AWS response.
        :param dict_src:
        :return:
        
        """

        init_options = {
            "ARN": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "ServerlessCacheName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "Description": self.init_default_attr,
            "CreateTime": self.init_default_attr,
            "Status": self.init_default_attr,
            "Engine": self.init_default_attr,
            "MajorEngineVersion": self.init_default_attr,
            "FullEngineVersion": self.init_default_attr,
            "SecurityGroupIds": self.init_default_attr,
            "Endpoint": self.init_default_attr,
            "ReaderEndpoint": self.init_default_attr,
            "SubnetIds": self.init_default_attr,
            "SnapshotRetentionLimit": self.init_default_attr,
            "DailySnapshotTime": self.init_default_attr,
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

    def generate_modify_request(self, desired_state):
        """
        Standard.

        :param desired_state:
        :return:
        """

        raise NotImplementedError("Do the same as in elasticache replication group")

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
