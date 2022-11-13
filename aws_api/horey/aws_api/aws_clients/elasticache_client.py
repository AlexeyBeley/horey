"""
AWS clietn to handle service API requests.
"""
import pdb


from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.elasticache_cluster import ElasticacheCluster
from horey.aws_api.aws_services_entities.elasticache_cache_parameter_group import (
    ElasticacheCacheParameterGroup,
)
from horey.aws_api.aws_services_entities.elasticache_cache_subnet_group import (
    ElasticacheCacheSubnetGroup,
)
from horey.aws_api.aws_services_entities.elasticache_cache_security_group import (
    ElasticacheCacheSecurityGroup,
)
from horey.aws_api.aws_services_entities.elasticache_replication_group import (
    ElasticacheReplicationGroup,
)


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

        for dict_src in self.execute(
            self.client.describe_cache_clusters, "CacheClusters"
        ):
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

        for dict_src in self.execute(
            self.client.describe_cache_parameter_groups, "CacheParameterGroups"
        ):
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

        for dict_src in self.execute(
            self.client.describe_cache_subnet_groups, "CacheSubnetGroups"
        ):
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

        for dict_src in self.execute(
            self.client.describe_replication_groups, "ReplicationGroups"
        ):
            obj = ElasticacheReplicationGroup(dict_src)
            final_result.append(obj)

        return final_result

    def get_all_cache_security_groups(self, region=None):
        """
        Get all cache_security_groups in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_cache_security_groups(region)
        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_cache_security_groups(region)

        return final_result

    def get_region_cache_security_groups(self, region, cache_security_group_name=None):
        AWSAccount.set_aws_region(region)

        final_result = list()
        filters_req = (
            {"CacheSecurityGroupName": cache_security_group_name}
            if cache_security_group_name is not None
            else None
        )
        for dict_src in self.execute(
            self.client.describe_cache_security_groups,
            "CacheSecurityGroups",
            filters_req=filters_req,
        ):
            obj = ElasticacheCacheSecurityGroup(dict_src)
            final_result.append(obj)

        return final_result

    def test(self):
        ret = list(
            self.execute(self.client.describe_service_updates, "", raw_data=True)
        )

        # describe_cache_parameters() #CacheParameterGroupName

        # describe_engine_default_parameters() #CacheParameterGroupFamily
        # ret = list(self.execute(self.client.describe_global_replication_groups, "GlobalReplicationGroups", raw_data=True))
        # describe_reserved_cache_nodes() #ReservedCacheNodes
        # ret = list(self.execute(self.client.describe_reserved_cache_nodes_offerings, "ReservedCacheNodesOfferings"))

        # ret = list(self.execute(self.client.describe_service_updates, "ServiceUpdates"))
        # ret = list(self.execute(self.client.describe_snapshots, "Snapshots"))
        # ret = list(self.execute(self.client.describe_update_actions, "UpdateActions"))
        # ret = list(self.execute(self.client.describe_user_groups, "UserGroups"))
        # ret = list(self.execute(self.client.describe_users, "Users"))
        # ret = list(self.execute(self.client.list_allowed_node_type_modifications, "", raw_data=True)) #CacheClusterId or ReplicationGroupId
        # ret = list(self.execute(self.client.list_tags_for_resource, "", raw_data=True)) #ResourceName

    def provision_subnet_group(self, subnet_group):
        region_subnet_groups = self.get_region_cache_subnet_groups(subnet_group.region)
        for region_subnet_group in region_subnet_groups:
            if subnet_group.name == region_subnet_group.name:
                subnet_group.update_from_raw_response(region_subnet_group.dict_src)
                return

        AWSAccount.set_aws_region(subnet_group.region)
        response = self.provision_subnet_group_raw(
            subnet_group.generate_create_request()
        )
        subnet_group.update_from_raw_response(response)

    def provision_subnet_group_raw(self, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Creating redis_subnet_group: {request_dict}")
        for response in self.execute(
            self.client.create_cache_subnet_group,
            "CacheSubnetGroup",
            filters_req=request_dict,
        ):
            return response

    def provision_cluster(self, cluster):
        pdb.set_trace()
        region_clusters = self.get_region_clusters(cluster.region)
        for region_cluster in region_clusters:
            if cluster.id == region_cluster.id:
                cluster.update_from_raw_response(region_cluster.dict_src)

        AWSAccount.set_aws_region(cluster.region)
        response = self.provision_cluster_raw(cluster.generate_create_request())
        cluster.update_from_raw_response(response)

    def provision_cluster_raw(self, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Creating redis_cluster: {request_dict}")
        for response in self.execute(
            self.client.create_cache_cluster, "CacheCluster", filters_req=request_dict
        ):
            return response

    def provision_replication_group(self, replication_group):
        region_replication_groups = self.get_region_replication_groups(
            replication_group.region
        )
        for region_replication_group in region_replication_groups:
            if replication_group.id == region_replication_group.id:
                replication_group.update_from_raw_response(
                    region_replication_group.dict_src
                )
                return

        AWSAccount.set_aws_region(replication_group.region)
        response = self.provision_replication_group_raw(
            replication_group.generate_create_request()
        )
        replication_group.update_from_raw_response(response)

    def provision_replication_group_raw(self, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Creating redis_replication_group: {request_dict}")
        for response in self.execute(
            self.client.create_replication_group,
            "ReplicationGroup",
            filters_req=request_dict,
        ):
            return response

    def provision_security_group(self, security_group):
        pdb.set_trace()
        region_security_groups = self.get_region_cache_security_groups(
            security_group.region, cache_security_group_name=security_group.name
        )
        if len(region_security_groups) > 0:
            region_security_group = region_security_groups[0]
            request = security_group.generate_authorize_request(
                existing_security_group=region_security_group
            )
            if request:
                self.authorize_security_group_raw(request)
            security_group.update_from_raw_response(region_security_group.dict_src)
            return

        AWSAccount.set_aws_region(security_group.region)
        response = self.provision_security_group_raw(
            security_group.generate_create_request()
        )
        security_group.update_from_raw_response(response)

        request = security_group.generate_authorize_request()
        if request:
            self.authorize_security_group_raw(request)

    def provision_security_group_raw(self, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Creating redis_security_group: {request_dict}")
        for response in self.execute(
            self.client.create_cache_security_group,
            "CachesecurityGroup",
            filters_req=request_dict,
        ):
            return response

    def authorize_security_group_raw(self, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Authorizing redis_security_group: {request_dict}")
        for response in self.execute(
            self.client.authorize_cache_security_group_ingress,
            "CacheSecurityGroup",
            filters_req=request_dict,
        ):
            return response
