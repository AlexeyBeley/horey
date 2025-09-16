"""
AWS ElasticacheReplicationGroup representation
"""
from enum import Enum

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.common_utils.common_utils import CommonUtils


# pylint: disable= too-many-instance-attributes
class ElasticacheReplicationGroup(AwsObject):
    """
    Elasticache Cluster class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.security_group_ids = None
        self.description = None
        self.preferred_cache_cluster_azs = None
        self.cache_node_type = None
        self.engine = None
        self.status = None
        self.engine_version = None
        self.cache_parameter_group_name = None
        self.cache_subnet_group_name = None
        self.preferred_maintenance_window = None
        self.auto_minor_version_upgrade = None
        self.snapshot_retention_limit = None
        self.snapshot_window = None
        self.num_cache_clusters = None
        self.node_groups = []
        self.replication_group_description = None
        self.primary_cluster_id = None
        self.automatic_failover_enabled = None
        self.multi_az_enabled = None
        self.node_group_id = None
        self.cache_security_group_names = None
        self.notification_topic_arn = None
        self.notification_topic_status = None
        self.auth_token = None
        self.auth_token_update_strategy = None
        self.user_group_ids_to_add = None
        self.user_group_ids_to_remove = None
        self.remove_user_groups = None
        self.transit_encryption_mode = None
        self.snapshotting_cluster_id = None
        self.log_delivery_configurations = []
        self.ip_discovery = None
        self.transit_encryption_enabled = None
        self.cluster_mode = None

        self.request_key_to_attribute_mapping = {"ARN": "arn", "ReplicationGroupId": "id"}

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
            "MultiAZ": lambda x, y: self.init_default_attr(x, y, formatted_name="multi_az_enabled"),
            "SnapshotRetentionLimit": self.init_default_attr,
            "SnapshotWindow": self.init_default_attr,
            "ClusterEnabled": self.init_default_attr,
            "CacheNodeType": self.init_default_attr,
            "AuthTokenEnabled": self.init_default_attr,
            "TransitEncryptionEnabled": self.init_default_attr,
            "AtRestEncryptionEnabled": self.init_default_attr,
            "DataTiering": self.init_default_attr,
            "AutoMinorVersionUpgrade": self.init_default_attr,
            "NetworkType": self.init_default_attr,
            "IpDiscovery": self.init_default_attr,
            "ClusterMode": self.init_default_attr,
            "Engine": self.init_default_attr,
            "ReplicationGroupCreateTime": self.init_default_attr,
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

    def get_primary_endpoint_address(self):
        """
        Standard.

        :return:
        """

        if len(self.node_groups) != 1:
            raise NotImplementedError(f"len(self.node_groups) != 1: {self.node_groups}")
        return self.node_groups[0]["PrimaryEndpoint"]["Address"]

    def get_status(self):
        """
        For the status_waiter.

        :return:
        """

        if self.status is None:
            raise self.UndefinedStatusError("Status")

        return self.Status.__members__[CommonUtils.camel_case_to_snake_case(self.status).upper()]

    class Status(Enum):
        """
        Standard
        """

        CREATING = 0
        AVAILABLE = 1
        MODIFYING = 2
        DELETING = 3
        CREATE_FAILED = 4
        SNAPSHOTTING = 5

    def generate_modify_request(self, desired_state):
        """
        Standard.

        :param desired_state:
        :return:
        """

        response = self.generate_request_aws_object_modify(desired_state, ["ReplicationGroupId"],
                                                       optional=["ReplicationGroupDescription",
                                                                 "PrimaryClusterId",
                                                                 "AutomaticFailoverEnabled",
                                                                 "MultiAZEnabled",
                                                                 "NodeGroupId",
                                                                 "CacheSecurityGroupNames",
                                                                 "SecurityGroupIds",
                                                                 "PreferredMaintenanceWindow",
                                                                 "NotificationTopicArn",
                                                                 "CacheParameterGroupName",
                                                                 "NotificationTopicStatus",
                                                                 "Engine",
                                                                 "EngineVersion",
                                                                 "AutoMinorVersionUpgrade",
                                                                 "SnapshotRetentionLimit",
                                                                 "SnapshotWindow",
                                                                 "CacheNodeType",
                                                                 "AuthToken",
                                                                 "AuthTokenUpdateStrategy",
                                                                 "UserGroupIdsToAdd",
                                                                 "UserGroupIdsToRemove",
                                                                 "RemoveUserGroups",
                                                                 "LogDeliveryConfigurations",
                                                                 "IpDiscovery",
                                                                 "TransitEncryptionEnabled",
                                                                 "TransitEncryptionMode",
                                                                 "ClusterMode"],
                                                       request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)
        if response:
            response["ApplyImmediately"] = True

        mz_enabled = response.get("MultiAZEnabled")
        if mz_enabled is not None and not isinstance(mz_enabled, bool):
            if mz_enabled == "enabled":
                response["MultiAZEnabled"] = True
            elif mz_enabled == "disabled":
                response["MultiAZEnabled"] = False
            else:
                raise ValueError(f"MultiAZEnabled in {response}")

        return response

    def generate_create_request(self):
        """
        Standard.
        :return:
        """

        raise NotImplementedError("Fix generate_create_request_old to be same logic as in modify function")

    def generate_create_request_old(self):
        """
        Standard.
        :return:
        """

        request = {"ReplicationGroupId": self.id, "ReplicationGroupDescription": self.description,
                   "PreferredCacheClusterAZs": self.preferred_cache_cluster_azs, "CacheNodeType": self.cache_node_type,
                   "Engine": self.engine, "EngineVersion": self.engine_version, "Tags": self.tags}

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
