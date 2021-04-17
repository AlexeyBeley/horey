"""
AWS lambda client to handle lambda service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.cloudfront_distribution import CloudfrontDistribution
from horey.aws_api.base_entities.aws_account import AWSAccount
import pdb

class CloudfrontClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """
    NEXT_PAGE_REQUEST_KEY = "Marker"
    NEXT_PAGE_RESPONSE_KEY = "NextMarker"
    NEXT_PAGE_INITIAL_KEY = ""

    def __init__(self):
        client_name = "cloudfront"
        super().__init__(client_name)

    def get_all_distributions(self, full_information=True):
        """
        Get all lambda in all regions
        :param full_information:
        :return:
        """
        final_result = list()

        for response in self.execute(self.client.list_distributions, "DistributionList", internal_starting_token=True):
            if response["Quantity"] == 0:
                continue

            for item in response["Items"]:
                obj = CloudfrontDistribution(item)
                final_result.append(obj)

            if full_information:
                pass

        return final_result
