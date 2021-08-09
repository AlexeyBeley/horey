"""
AWS lambda client to handle lambda service API requests.
"""
import pdb
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.ecs_capacity_provider import ECSCapacityProvider


class ECSClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "ecs"
        super().__init__(client_name)

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
