"""
AWS clietn to handle service API requests.
"""

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

    # pylint: disable= too-many-arguments
    def yield_clusters(self, region=None, update_info=False, filters_req=None):
        """
        Yield clusters

        :return:
        """

        regional_fetcher_generator = self.yield_clusters_raw
        for obj in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  ElasticacheCluster,
                                                  update_info=update_info,
                                                  regions=[region] if region else None,
                                                  filters_req=filters_req):
            yield obj

    def yield_clusters_raw(self, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.client.describe_cache_clusters, "CacheClusters",
                filters_req=filters_req,
                exception_ignore_callback=lambda error: "RepositoryNotFoundException"
            in repr(error)
        ):
            yield dict_src

    def get_all_clusters(self, region=None):
        """
        Get all clusters in all regions.
        :return:
        """

        return list(self.yield_clusters(region=region))

    def get_region_clusters(self, region):
        """
        Get clusters.

        :param region:
        :return:
        """

        return list(self.yield_clusters(region=region))

    def get_all_cache_parameter_groups(self, region=None):
        """
        Get all parameter_groups in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_cache_parameter_groups(region)
        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_cache_parameter_groups(_region)

        return final_result

    def get_region_cache_parameter_groups(self, region):
        """
        Stanard.

        :param region:
        :return:
        """
        AWSAccount.set_aws_region(region)

        final_result = []

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
        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_cache_subnet_groups(_region)

        return final_result

    def get_region_cache_subnet_groups(self, region):
        """
        Stanard.

        :param region:
        :return:
        """
        AWSAccount.set_aws_region(region)

        final_result = []

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
        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_replication_groups(_region)

        return final_result

    def get_region_replication_groups(self, region):
        """
        Stanard.

        :param region:
        :return:
        """
        AWSAccount.set_aws_region(region)

        final_result = []

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
        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_cache_security_groups(_region)

        return final_result

    def get_region_cache_security_groups(self, region, cache_security_group_name=None):
        """
        Standard.

        :param region:
        :param cache_security_group_name:
        :return:
        """
        AWSAccount.set_aws_region(region)

        final_result = []
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

    def provision_subnet_group(self, subnet_group):
        """
        Stanard.

        :param subnet_group:
        :return:
        """
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
        """
        Standard.

        :param cluster:
        :return:
        """
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
        """
        Standard.

        :param replication_group:
        :return:
        """
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
