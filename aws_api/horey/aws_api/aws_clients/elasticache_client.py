"""
AWS clietn to handle service API requests.
"""
import pdb


from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.elasticache_cluster import ElasticacheCluster
from horey.aws_api.aws_services_entities.elasticache_cache_parameter_group import ElasticacheCacheParameterGroup
from horey.aws_api.aws_services_entities.elasticache_cache_subnet_group import ElasticacheCacheSubnetGroup
from horey.aws_api.aws_services_entities.elasticache_replication_group import ElasticacheReplicationGroup

from horey.h_logger import get_logger


logger = get_logger()


class ElasticacheClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """
    NEXT_PAGE_REQUEST_KEY = "Marker"
    NEXT_PAGE_RESPONSE_KEY = "Marker"

    def __init__(self):
        client_name = "elasticache"
        super().__init__(client_name)

    def get_all_clusters(self, region=None):
        """
        Get all clusters in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_clusters(region)
        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_clusters(region)

        return final_result

    def get_region_clusters(self, region):
        AWSAccount.set_aws_region(region)

        final_result = list()

        pdb.set_trace()
        for dict_src in self.execute(self.client.describe_cache_clusters, "CacheClusters"):
            pdb.set_trace()
            obj = ElasticacheCluster(dict_src)
            final_result.append(obj)

        return final_result
    
    def get_all_cache_parameter_groups(self, region=None):
        """
        Get all parameter_groups in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_cache_parameter_groups(region)
        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_cache_parameter_groups(region)

        return final_result

    def get_region_cache_parameter_groups(self, region):
        AWSAccount.set_aws_region(region)

        final_result = list()

        pdb.set_trace()
        for dict_src in self.execute(self.client.describe_cache_parameter_groups, "CacheParameterGroups"):
            pdb.set_trace()
            obj = ElasticacheCacheParameterGroup(dict_src)
            final_result.append(obj)

        return final_result
    
    def get_all_cache_subnet_groups(self, region=None):
        """
        Get all subnet_groups in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_cache_subnet_groups(region)
        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_cache_subnet_groups(region)

        return final_result

    def get_region_cache_subnet_groups(self, region):
        AWSAccount.set_aws_region(region)

        final_result = list()

        pdb.set_trace()
        for dict_src in self.execute(self.client.describe_cache_subnet_groups, "CacheSubnetGroups"):
            pdb.set_trace()
            obj = ElasticacheCacheSubnetGroup(dict_src)
            final_result.append(obj)

        return final_result

    def get_all_replication_groups(self, region=None):
        """
        Get all replication_groups in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_replication_groups(region)
        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_replication_groups(region)

        return final_result

    def get_region_replication_groups(self, region):
        AWSAccount.set_aws_region(region)

        final_result = list()

        pdb.set_trace()
        for dict_src in self.execute(self.client.describe_cache_replication_groups, "ReplicationGroups"):
            pdb.set_trace()
            obj = ElasticacheReplicationGroup(dict_src)
            final_result.append(obj)

        return final_result
    
    def test(self):
        ret = list(self.execute(self.client.describe_service_updates, "", raw_data=True))


        #describe_cache_parameters() #CacheParameterGroupName

        #describe_engine_default_parameters() #CacheParameterGroupFamily
        #ret = list(self.execute(self.client.describe_global_replication_groups, "GlobalReplicationGroups", raw_data=True))
        # describe_reserved_cache_nodes() #ReservedCacheNodes
        #ret = list(self.execute(self.client.describe_reserved_cache_nodes_offerings, "ReservedCacheNodesOfferings"))

        #ret = list(self.execute(self.client.describe_service_updates, "ServiceUpdates"))
        #ret = list(self.execute(self.client.describe_snapshots, "Snapshots"))
        #ret = list(self.execute(self.client.describe_update_actions, "UpdateActions"))
        #ret = list(self.execute(self.client.describe_user_groups, "UserGroups"))
        #ret = list(self.execute(self.client.describe_users, "Users"))
        #ret = list(self.execute(self.client.list_allowed_node_type_modifications, "", raw_data=True)) #CacheClusterId or ReplicationGroupId
        #ret = list(self.execute(self.client.list_tags_for_resource, "", raw_data=True)) #ResourceName
