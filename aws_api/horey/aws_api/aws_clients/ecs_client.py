"""
AWS lambda client to handle lambda service API requests.
"""
import pdb
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.ecs_cluster import ECSCluster
from horey.aws_api.aws_services_entities.ecs_capacity_provider import ECSCapacityProvider


class ECSClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "ecs"
        super().__init__(client_name)

    def register_task_definition(self, request_dict):
        for response in self.execute(self.client.register_task_definition, "taskDefinition", filters_req=request_dict):
            pdb.set_trace()

    def create_cluster(self, request_dict):
        for response in self.execute(self.client.create_cluster, "cluster", filters_req=request_dict):
            pdb.set_trace()

    def run_task(self, request_dict):
        for response in self.execute(self.client.run_task, "tasks", filters_req=request_dict):
            return response

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

    def get_all_capacity_providers(self, region=None):
        """
        Get all capacity_providers in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_capacity_providers(region)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_capacity_providers(region)

        return final_result

    def get_region_capacity_providers(self, region):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.describe_capacity_providers, "capacityProviders"):
            obj = ECSCapacityProvider(dict_src)
            final_result.append(obj)

        return final_result

    def get_region_clusters(self, region):
        AWSAccount.set_aws_region(region)

        final_result = list()
        clusters_arns = []
        for cluster_arn in self.execute(self.client.list_clusters, "clusterArns"):
            clusters_arns.append(cluster_arn)

        if len(clusters_arns) > 100:
            raise NotImplementedError("""clusters (list) -- A list of up to 100 cluster names or full cluster 
            Amazon Resource Name (ARN) entries. If you do not specify a cluster, the default cluster is assumed.""")

        filter_req = {"clusters": clusters_arns,
                      "include": ["ATTACHMENTS", "CONFIGURATIONS", "SETTINGS", "STATISTICS", "TAGS"]}

        for dict_src in self.execute(self.client.describe_clusters, "clusters", filters_req=filter_req):
            obj = ECSCluster(dict_src)
            final_result.append(obj)

        return final_result