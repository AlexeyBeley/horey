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

    def __init__(self, aws_account=None):
        client_name = "elasticache"
        super().__init__(client_name, aws_account=aws_account)

    # pylint: disable= too-many-arguments
    def yield_clusters(self, region=None, update_info=False, filters_req=None):
        """
        Yield clusters

        :return:
        """

        regional_fetcher_generator = self.yield_clusters_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            ElasticacheCluster,
                                                            update_info=update_info,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_clusters_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
                self.get_session_client(region=region).describe_cache_clusters, "CacheClusters",
                filters_req=filters_req
        )

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
        Standard.

        :param region:
        :return:
        """

        final_result = []

        for dict_src in self.execute(
                self.get_session_client(region=region).describe_cache_parameter_groups, "CacheParameterGroups"
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
        Standard.

        :param region:
        :return:
        """

        final_result = []

        for dict_src in self.execute(
                self.get_session_client(region=region).describe_cache_subnet_groups, "CacheSubnetGroups"
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
        Standard.

        :param region:
        :return:
        """

        final_result = []

        for dict_src in self.execute(
                self.get_session_client(region=region).describe_replication_groups, "ReplicationGroups"
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

        final_result = []
        filters_req = (
            {"CacheSecurityGroupName": cache_security_group_name}
            if cache_security_group_name is not None
            else None
        )
        for dict_src in self.execute(
                self.get_session_client(region=region).describe_cache_security_groups,
                "CacheSecurityGroups",
                filters_req=filters_req,
        ):
            obj = ElasticacheCacheSecurityGroup(dict_src)
            final_result.append(obj)

        return final_result

    def provision_subnet_group(self, subnet_group):
        """
        Standard

        :param subnet_group:
        :return:
        """
        region_subnet_groups = self.get_region_cache_subnet_groups(subnet_group.region)
        for region_subnet_group in region_subnet_groups:
            if subnet_group.name == region_subnet_group.name:
                subnet_group.update_from_raw_response(region_subnet_group.dict_src)
                return

        response = self.provision_subnet_group_raw(subnet_group.region,
                                                   subnet_group.generate_create_request()
                                                   )
        subnet_group.update_from_raw_response(response)

    def provision_subnet_group_raw(self, region, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Creating redis_subnet_group: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_cache_subnet_group,
                "CacheSubnetGroup",
                filters_req=request_dict,
        ):
            self.clear_cache(ElasticacheCacheSubnetGroup)
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

        response = self.provision_cluster_raw(cluster.region, cluster.generate_create_request())
        cluster.update_from_raw_response(response)

    def provision_cluster_raw(self, region, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Creating redis_cluster: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_cache_cluster, "CacheCluster", filters_req=request_dict
        ):
            self.clear_cache(ElasticacheCluster)
            return response

    def yield_replication_groups(self, region=None, update_info=False, filters_req=None):
        """
        Yield clusters

        :return:
        """

        regional_fetcher_generator = self.yield_replication_groups_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            ElasticacheReplicationGroup,
                                                            update_info=update_info,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_replication_groups_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
                self.get_session_client(region=region).describe_replication_groups, "ReplicationGroups",
                filters_req=filters_req
        )

    def provision_replication_group(self, desired_replication_group: ElasticacheReplicationGroup):
        """
        Standard.

        :param desired_replication_group:
        :return:
        """

        existing_replication_group = ElasticacheReplicationGroup({})
        existing_replication_group.region = desired_replication_group.region
        existing_replication_group.id = desired_replication_group.id
        if not self.update_replication_group_information(existing_replication_group):
            self.provision_replication_group_raw(desired_replication_group.region,
                                                        desired_replication_group.generate_create_request()
                                                        )
        else:
            request = existing_replication_group.generate_modify_request(desired_replication_group)
            if request is None:
                return desired_replication_group.update_from_attrs(existing_replication_group)

            breakpoint()
            self.modify_replication_group_raw(desired_replication_group.region, request)

        self.wait_for_status(
            desired_replication_group,
            lambda replication_group:  self.update_replication_group_information(replication_group, full_information=False),
            [desired_replication_group.Status.AVAILABLE],
            [desired_replication_group.Status.CREATING,
             desired_replication_group.Status.MODIFYING,
             desired_replication_group.Status.SNAPSHOTTING],
            [
                desired_replication_group.Status.DELETING,
                desired_replication_group.Status.CREATE_FAILED,
            ], timeout=30*60
        )
        return True

    def update_replication_group_information(self, replication_group, full_information=True):
        """
        Standard

        :param full_information:
        :param replication_group:
        :return:
        """

        replication_groups = list(self.yield_replication_groups(region=replication_group.region,
                                                                filters_req={"ReplicationGroupId":replication_group.id}))
        if len(replication_groups) == 0:
            return False

        if len(replication_groups) != 1:
            raise ValueError(f"Found more than 1: {replication_groups} replication groups by id {replication_group.id}"
                             f" in region {replication_group.region.region_mark}")

        if not replication_group.update_from_attrs(replication_groups[0]):
            raise RuntimeError("Was not able to update")

        if not full_information:
            return True

        replication_group.security_group_ids = []
        for member_cluster_id in replication_group.member_clusters:
            clusters = list(self.yield_clusters(replication_group.region, update_info=True, filters_req={"CacheClusterId": member_cluster_id}))
            if len(clusters) != 1:
                raise RuntimeError(f"Expected single elasticache cluster, found {len(clusters)=}")
            cluster = clusters[0]
            for sg in cluster.security_groups:
                if sg["Status"] != "active":
                    continue
                if sg["SecurityGroupId"] in replication_group.security_group_ids:
                    continue
                replication_group.security_group_ids.append(sg["SecurityGroupId"])

            if replication_group.engine_version is not None and replication_group.engine_version != cluster.engine_version:
                raise ValueError(f"{cluster.id=}, {replication_group.engine_version=}, {cluster.engine_version=}")
            replication_group.engine_version = cluster.engine_version

            if replication_group.preferred_maintenance_window is not None and replication_group.preferred_maintenance_window != cluster.preferred_maintenance_window:
                raise ValueError(f"{cluster.id=}, {replication_group.preferred_maintenance_window=}, {cluster.preferred_maintenance_window=}")
            replication_group.preferred_maintenance_window = cluster.preferred_maintenance_window

            if (cluster.cache_parameter_group["ParameterApplyStatus"] != "in-sync") or \
                    len(cluster.cache_parameter_group["CacheNodeIdsToReboot"]) > 0:
                raise RuntimeError(f"{cluster.dict_src}")

            if replication_group.cache_parameter_group_name is not None and replication_group.cache_parameter_group_name != cluster.cache_parameter_group["CacheParameterGroupName"]:
                raise ValueError(f"{cluster.id=}, {replication_group.cache_parameter_group_name=}, {cluster.cache_parameter_group=}")
            replication_group.cache_parameter_group_name = cluster.cache_parameter_group["CacheParameterGroupName"]

        return True

    def provision_replication_group_raw(self, region, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Creating redis_replication_group: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_replication_group,
                "ReplicationGroup",
                filters_req=request_dict,
        ):
            self.clear_cache(ElasticacheReplicationGroup)
            return response

    def modify_replication_group_raw(self, region, request_dict):
        """
        Returns ARN

        """

        logger.info(f"Modifying redis_replication_group: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).modify_replication_group,
                "ReplicationGroup",
                filters_req=request_dict,
        ):
            self.clear_cache(ElasticacheReplicationGroup)
            return response

    def describe_cache_engine_versions_raw(self, region, filters_req):
        """
        Standard.

        :param filters_req:
        :param region:
        :return:
        """

        logger.info("Describe_cache_engine_versions_raw.")
        return list(self.execute(
            self.get_session_client(region=region).describe_cache_engine_versions,
            "CacheEngineVersions",
            filters_req=filters_req
        ))

    def get_latest_engine_version_and_param_family(self, region, str_engine):
        """
        Get engine and latest param family for it

        :param engine:
        :return:
        """
        engine_raw = self.get_latest_engine_version(region, str_engine)
        params_raw = self.get_latest_parameter_group(region, engine_raw["CacheParameterGroupFamily"])
        return engine_raw, params_raw

    def get_latest_engine_version(self, region, str_engine):
        """
        Find the latest engine version and default configs.

        :param engine:
        :return:
        """

        versions_dicts = self.describe_cache_engine_versions_raw(region, {"Engine": str_engine})
        versions_dict = {version_dict["EngineVersion"]: version_dict for version_dict in versions_dicts}

        reached_end = False
        while len(versions_dict) > 1:
            if reached_end:
                raise RuntimeError("reached_end")
            if any("." not in key for key in versions_dict):
                reached_end = True
                if any("." in key for key in versions_dict):
                    raise RuntimeError(versions_dict)
            max_sub_version = max(int(key.split(".")[0]) for key in versions_dict)
            versions_dict = {key[key.find(".") + 1:]: value for key, value in versions_dict.items() if
                             int(key.split(".")[0]) == max_sub_version}

        return list(versions_dict.values())[0]

    def get_latest_parameter_group(self, region, family_name):
        """
        Fetch and find max.

        :param family_name:
        :return:
        """
        versions_dicts = list(self.execute(self.get_session_client(region=region).describe_cache_parameter_groups,
                                           "CacheParameterGroups"))
        ret = []
        for version in versions_dicts:
            if version["CacheParameterGroupFamily"] != family_name:
                continue
            if "cluster mode on" in version["Description"]:
                continue
            ret.append(version)
        if len(ret) != 1:
            raise RuntimeError(ret)
        return ret[0]
