"""
AWS lambda client to handle lambda service API requests.
"""

from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.eks_cluster import EKSCluster
from horey.aws_api.aws_services_entities.eks_addon import EKSAddon
from horey.aws_api.aws_services_entities.eks_fargate_profile import EKSFargateProfile

from horey.h_logger import get_logger

logger = get_logger()


class EKSClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        """
        ret = self.get_all_clusters()

        list_fargate_profiles = list(self.execute(self.client.list_fargate_profiles, "fargateProfileNames", filters_req={"clusterName": ret[0].name}))
        list_identity_provider_configs = list(self.execute(self.client.list_identity_provider_configs, "identityProviderConfigs", filters_req={"clusterName": ret[0].name}))
        list_nodegroups = list(self.execute(self.client.list_nodegroups, "nodegroups", filters_req={"clusterName": ret[0].name}))
        """
        client_name = "eks"
        super().__init__(client_name)

    # region cluster
    def get_all_clusters(self, region=None, full_information=True):
        """
        Get all clusters in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_clusters(
                region, full_information=full_information
            )

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_clusters(
                _region, full_information=full_information
            )

        return final_result

    def get_region_clusters(self, region, full_information=True):
        """
        Region specific state machines.

        :param region:
        :param full_information:
        :return:
        """

        final_result = []
        AWSAccount.set_aws_region(region)
        for name in self.execute(
            self.client.list_clusters, "clusters"
        ):
            obj = EKSCluster({"name": name})
            obj.region = region
            final_result.append(obj)
            if full_information:
                self.update_cluster_info(obj)

        return final_result

    def update_cluster_info(self, obj):
        """
        Update current status.

        :param obj:
        :return:
        """

        AWSAccount.set_aws_region(obj.region)
        for dict_src in self.execute(
                self.client.describe_cluster, "cluster", filters_req={"name": obj.name}
        ):
            obj.update_from_raw_response(dict_src)

    def provision_cluster(self, cluster: EKSCluster):
        """
        Provision from object.

        :param cluster:
        :return:
        """

        region_clusters = self.get_region_clusters(
            cluster.region
        )
        for region_cluster in region_clusters:
            if (
                region_cluster.name == cluster.name
            ):
                cluster.update_from_raw_response(
                    region_cluster.dict_src
                )
                return
        AWSAccount.set_aws_region(cluster.region)
        response = self.provision_cluster_raw(
            cluster.generate_create_request()
        )
        cluster.update_from_raw_response(response)

    def provision_cluster_raw(self, request_dict):
        """
        Provision from raw request.

        :param request_dict:
        :return:
        """

        logger.info(f"Creating cluster: {request_dict}")
        for response in self.execute(
            self.client.create_cluster,
            None,
            raw_data=True,
            filters_req=request_dict,
        ):
            del response["ResponseMetadata"]
            return response

    # endregion

    # region addon
    def get_all_addons(self, region=None, full_information=True):
        """
        Get all addons in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_addons(
                region, full_information=full_information
            )

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_addons(
                _region, full_information=full_information
            )

        return final_result

    def get_region_addons(self, region, full_information=True):
        """
        Region specific state machines.

        :param region:
        :param full_information:
        :return:
        """

        final_result = []
        clusters = self.get_region_clusters(region)

        for cluster in clusters:
            final_result += self.get_cluster_addons(cluster, full_information=full_information)

        return final_result

    def get_cluster_addons(self, cluster, full_information=True):
        """
        Region specific state machines.

        :param cluster:
        :param full_information:
        :return:
        """

        final_result = []
        AWSAccount.set_aws_region(cluster.region)
        for name in self.execute(
                self.client.list_addons, "addons", filters_req={"clusterName": cluster.name}
        ):
            obj = EKSAddon({"addonName": name, "clusterName": cluster.name})
            final_result.append(obj)
            if full_information:
                self.update_addon_info(obj)

        return final_result

    def update_addon_info(self, obj):
        """
        Update current status.

        :param obj:
        :return:
        """

        for dict_src in self.execute(
                self.client.describe_addon, "addon", filters_req={"clusterName": obj.cluster_name, "addonName": obj.name}
        ):
            obj.update_from_raw_response(dict_src)

    def provision_addon(self, addon: EKSCluster):
        """
        Provision from object.

        :param addon:
        :return:
        """

        region_addons = self.get_region_addons(
            addon.region
        )
        for region_addon in region_addons:
            if (
                    region_addon.name == addon.name
            ):
                addon.update_from_raw_response(
                    region_addon.dict_src
                )
                return
        AWSAccount.set_aws_region(addon.region)
        response = self.provision_addon_raw(
            addon.generate_create_request()
        )
        addon.update_from_raw_response(response)

    def provision_addon_raw(self, request_dict):
        """
        Provision from raw request.

        :param request_dict:
        :return:
        """

        logger.info(f"Creating addon: {request_dict}")
        for response in self.execute(
                self.client.create_addon,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            del response["ResponseMetadata"]
            return response

    # endregion

    # region fargate_profile
    def get_all_fargate_profiles(self, region=None, full_information=True):
        """
        Get all fargate_profiles in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_fargate_profiles(
                region, full_information=full_information
            )

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_fargate_profiles(
                _region, full_information=full_information
            )

        return final_result

    def get_region_fargate_profiles(self, region, full_information=True):
        """
        Region specific fargate_profiles.

        :param region:
        :param full_information:
        :return:
        """

        final_result = []
        clusters = self.get_region_clusters(region)

        for cluster in clusters:
            final_result += self.get_cluster_fargate_profiles(cluster, full_information=full_information)

        return final_result

    def get_cluster_fargate_profiles(self, cluster, full_information=True):
        """
        Region specific fargate_profiles.

        :param cluster:
        :param full_information:
        :return:
        """

        final_result = []
        AWSAccount.set_aws_region(cluster.region)
        for name in self.execute(
                self.client.list_fargate_profiles, "fargateProfileNames", filters_req={"clusterName": cluster.name}
        ):
            obj = EKSFargateProfile({"fargateProfileName": name, "clusterName": cluster.name})
            final_result.append(obj)
            if full_information:
                self.update_fargate_profile_info(obj)

        return final_result

    def update_fargate_profile_info(self, obj):
        """
        Update current status.

        :param obj:
        :return:
        """

        for dict_src in self.execute(
                self.client.describe_fargate_profile, "fargateProfile", filters_req={"clusterName": obj.cluster_name, "fargateProfileName": obj.name}
        ):
            obj.update_from_raw_response(dict_src)

    def provision_fargate_profile(self, fargate_profile: EKSFargateProfile):
        """
        Provision from object.

        :param fargate_profile:
        :return:
        """
        fargate_profile_current = EKSFargateProfile({"fargateProfileName": fargate_profile.name,
                                                     "clusterName": fargate_profile.cluster_name})
        fargate_profile_current.region = fargate_profile.region
        self.update_fargate_profile_info(
            fargate_profile_current
        )
        if fargate_profile_current.arn:
            self.update_fargate_profile_info(
                fargate_profile
            )
            return
        AWSAccount.set_aws_region(fargate_profile.region)
        response = self.provision_fargate_profile_raw(
            fargate_profile.generate_create_request()
        )
        fargate_profile.update_from_raw_response(response)

    def provision_fargate_profile_raw(self, request_dict):
        """
        Provision from raw request.

        :param request_dict:
        :return:
        """

        logger.info(f"Creating fargate_profile: {request_dict}")
        for response in self.execute(
                self.client.create_fargate_profile,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            del response["ResponseMetadata"]
            return response

    def dispose_fargate_profile(self, fargate_profile: EKSFargateProfile):
        """
        Dispose.

        :return:
        """
        request_dict = {"clusterName": fargate_profile.cluster_name,
                        "fargateProfileName": fargate_profile.name}
        logger.info(f"Disposing fargate_profile: {request_dict}")
        for response in self.execute(
                self.client.delete_fargate_profile,
                "fargateProfile",
                filters_req=request_dict,
        ):
            return response

    # endregion
