"""
AWS lambda client to handle lambda service API requests.
"""
import pdb
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.aws_api.aws_services_entities.ecs_cluster import ECSCluster
from horey.aws_api.aws_services_entities.ecs_service import ECSService
from horey.aws_api.aws_services_entities.ecs_capacity_provider import ECSCapacityProvider
from horey.aws_api.aws_services_entities.ecs_task_definition import ECSTaskDefinition


from horey.h_logger import get_logger
logger = get_logger()


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
    
    def provision_capacity_provider(self, capacity_provider):
        """
        self.client.delete_capacity_provider(capacityProvider='test-capacity-provider')
        """
        region_objects = self.get_region_capacity_providers(capacity_provider.region)
        for region_object in region_objects:
            if region_object.name == capacity_provider.name:
                capacity_provider.update_from_raw_response(region_object.dict_src)
                return

        AWSAccount.set_aws_region(capacity_provider.region)
        response = self.provision_capacity_provider_raw(capacity_provider.generate_create_request())
        capacity_provider.update_from_raw_response(response)

    def provision_capacity_provider_raw(self, request_dict):
        logger.info(f"Creating ECS Capacity Provider: {request_dict}")
        for response in self.execute(self.client.create_capacity_provider, "capacityProvider", filters_req=request_dict):
            return response
        
    def provision_cluster(self, cluster):
        """
        self.client.delete_cluster(capacityProvider='test-capacity-provider')
        """
        region_objects = self.get_region_clusters(cluster.region)
        for region_object in region_objects:
            if region_object.name == cluster.name:
                cluster.update_from_raw_response(region_object.dict_src)
                return

        AWSAccount.set_aws_region(cluster.region)
        response = self.provision_cluster_raw(cluster.generate_create_request())
        cluster.update_from_raw_response(response)

    def provision_cluster_raw(self, request_dict):
        logger.info(f"Creating ECS Capacity Provider: {request_dict}")
        for response in self.execute(self.client.create_cluster, "cluster", filters_req=request_dict):
            return response

    def get_all_services(self, cluster):
        filters_req = {"cluster": cluster.name}
        AWSAccount.set_aws_region(cluster.region)

        final_result = []
        service_arns = []

        for dict_src in self.execute(self.client.list_services, "serviceArns", filters_req=filters_req):
            service_arns.append(dict_src)

        if len(service_arns) == 0:
            return []

        if len(service_arns) > 10:
            raise NotImplementedError()
        filters_req["services"] = service_arns
        for dict_src in self.execute(self.client.describe_services, "services", filters_req=filters_req):
            final_result.append(ECSService(dict_src))

        return final_result

    def get_all_task_definitions(self, region=None):
        if region is not None:
            return self.get_region_task_definitions(region)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_task_definitions(region)

        return final_result

    def get_region_task_definitions(self, region, family_prefix=None):
        list_arns = list()
        AWSAccount.set_aws_region(region)
        filters_req = dict()
        if family_prefix is not None:
            filters_req["familyPrefix"] = family_prefix

        for dict_src in self.execute(self.client.list_task_definitions, "taskDefinitionArns", filters_req=filters_req):
            list_arns.append(dict_src)

        if len(list_arns) == 0:
            return []

        final_result = list()
        for arn in list_arns:
            filters_req = {"taskDefinition": arn, "include": ['TAGS']}
            for dict_src in self.execute(self.client.describe_task_definition, "taskDefinition", filters_req=filters_req):
                final_result.append(ECSTaskDefinition(dict_src))

        return final_result

    def provision_ecs_task_definition(self, task_definition):
        #region_objects = self.get_region_task_definitions(task_definition.region, family_prefix=task_definition.family)
        #for region_object in region_objects:
        #    pdb.set_trace()
        #    if region_object.name == task_definition.name:
        #        task_definition.update_from_raw_response(region_object.dict_src)
        #        return

        AWSAccount.set_aws_region(task_definition.region)
        response = self.provision_ecs_task_definition_raw(task_definition.generate_create_request())
        task_definition.update_from_raw_response(response)

    def provision_ecs_task_definition_raw(self, request_dict):
        logger.info(f"Creating ECS task definition: {request_dict}")
        for response in self.execute(self.client.register_task_definition, "taskDefinition", filters_req=request_dict):
            return response

    @staticmethod
    def get_cluster_from_arn(cluster_arn):
        cluster = ECSCluster({})
        cluster.name = cluster_arn.split(":")[-1].split("/")[-1]
        cluster.arn = cluster_arn
        cluster.region = Region.get_region(cluster_arn.split(":")[3])
        return cluster

    def provision_service(self, service):
        cluster = self.get_cluster_from_arn(service.cluster_arn)
        region_objects = self.get_all_services(cluster)
        for region_object in region_objects:
            pdb.set_trace()
            if region_object.name == service.name:
                service.update_from_raw_response(region_object.dict_src)
                return

        AWSAccount.set_aws_region(service.region)
        response = self.provision_service_raw(service.generate_create_request())
        service.update_from_raw_response(response)

    def provision_service_raw(self, request_dict):
        logger.info(f"Creating ECS Service: {request_dict}")
        for response in self.execute(self.client.create_service, "service", filters_req=request_dict):
            return response
