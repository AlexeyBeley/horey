"""
AWS lambda client to handle lambda service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.cloudfront_origin_access_identity import CloudfrontOriginAccessIdentity
from horey.aws_api.aws_services_entities.cloudfront_distribution import CloudfrontDistribution
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
    
    def provision_distribution(self, distribution):
        existing_distributions = self.get_all_distributions()
        for existing_distribution in existing_distributions:
            if existing_distribution.get_tagname(ignore_missing_tag=True) == distribution.get_tagname():
                distribution.update_from_raw_create(existing_distribution.dict_src)
                return

        response = self.provision_distribution_raw(distribution.generate_create_request_with_tags())

        distribution.update_from_raw_create(response)

    def provision_distribution_raw(self, request_dict):
        for response in self.execute(self.client.create_distribution_with_tags, "Distribution", filters_req=request_dict):
            return response

    def get_all_origin_access_identities(self, full_information=True):
        """
        :param full_information:
        :return:
        """
        final_result = list()

        for response in self.execute(self.client.list_cloud_front_origin_access_identities, "CloudFrontOriginAccessIdentityList", internal_starting_token=True):
            if response["Quantity"] == 0:
                continue

            for item in response["Items"]:
                obj = CloudfrontOriginAccessIdentity(item)
                final_result.append(obj)

            if full_information:
                pass

        return final_result
    
    def provision_origin_access_identity(self, origin_access_identity):
        existing_origin_access_identities = self.get_all_origin_access_identities()
        for existing_origin_access_identity in existing_origin_access_identities:
            if existing_origin_access_identity.comment == origin_access_identity.comment:
                origin_access_identity.id = existing_origin_access_identity.id
                return

        response = self.provision_origin_access_identity_raw(origin_access_identity.generate_create_request())
        origin_access_identity.id = response["Id"]

    def provision_origin_access_identity_raw(self, request_dict):
        for response in self.execute(self.client.create_cloud_front_origin_access_identity, "CloudFrontOriginAccessIdentity", filters_req=request_dict):
            return response

    def create_invalidation(self, distribution, paths):
        self.create_invalidation_raw(distribution.generate_create_invalidation(paths))

    def create_invalidation_raw(self, request):
        for response in self.execute(self.client.create_invalidation, "Invalidation", filters_req=request):
            return response
