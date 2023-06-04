"""
AWS lambda client to handle lambda service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.cloudfront_origin_access_identity import (
    CloudfrontOriginAccessIdentity,
)
from horey.aws_api.aws_services_entities.cloudfront_distribution import (
    CloudfrontDistribution,
)
from horey.h_logger import get_logger

logger = get_logger()


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
        final_result = []

        for response in self.execute(
            self.client.list_distributions,
            "DistributionList",
            internal_starting_token=True,
        ):
            if response["Quantity"] == 0:
                continue

            for item in response["Items"]:
                obj = CloudfrontDistribution(item)
                final_result.append(obj)

                if full_information:
                    for response_tags in self.execute(self.client.list_tags_for_resource, "Tags", filters_req={"Resource": obj.arn}):
                        obj.tags = response_tags["Items"]
                        obj.tags = response_tags["Items"]

        return final_result

    def provision_distribution(self, distribution: CloudfrontDistribution):
        """
        WARNING! Comment is being used to identify distributions. If you've
        provisioned multiple cloudfront distributions with the same comment -
        it might raise an issue.

        @param distribution:
        @return:
        """
        desired_distribution = CloudfrontDistribution(distribution.distribution_config)
        existing_distributions = self.get_all_distributions()
        for existing_distribution in existing_distributions:
            if existing_distribution.comment == desired_distribution.comment:
                breakpoint()
                existing_distribution_id = existing_distribution.dict_src['Id']
                existing_distribution_config = self.get_distribution_config(existing_distribution_id)
                existing_distribution_etag = existing_distribution_config['ETag']
                response = self.update_distribution_raw(
                    distribution.generate_update_request(existing_distribution_id, existing_distribution_etag)
                )
                distribution.update_from_raw_create(response)
                return
        response = self.provision_distribution_raw(
            distribution.generate_create_request_with_tags()
        )

        distribution.update_from_raw_create(response)

    def provision_distribution_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """
        logger.info(f"Creating distribution {request_dict}")
        for response in self.execute(
            self.client.create_distribution_with_tags,
            "Distribution",
            filters_req=request_dict,
        ):
            return response

    def update_distribution_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """
        logger.info(f"updating distribution {request_dict}")
        for response in self.execute(
                self.client.update_distribution,
                "Distribution",
                filters_req=request_dict,
        ):
            return response

    def get_all_origin_access_identities(self, full_information=True):
        """
        :param full_information:
        :return:
        """
        final_result = []

        for response in self.execute(
            self.client.list_cloud_front_origin_access_identities,
            "CloudFrontOriginAccessIdentityList",
            internal_starting_token=True,
        ):
            if response["Quantity"] == 0:
                continue

            for item in response["Items"]:
                obj = CloudfrontOriginAccessIdentity(item)
                final_result.append(obj)

            if full_information:
                pass

        return final_result

    def provision_origin_access_identity(self, origin_access_identity):
        """
        Standard.

        :param origin_access_identity:
        :return:
        """

        existing_origin_access_identities = self.get_all_origin_access_identities()
        for existing_origin_access_identity in existing_origin_access_identities:
            if (
                existing_origin_access_identity.comment
                == origin_access_identity.comment
            ):
                origin_access_identity.id = existing_origin_access_identity.id
                return

        response = self.provision_origin_access_identity_raw(
            origin_access_identity.generate_create_request()
        )
        origin_access_identity.id = response["Id"]

    def provision_origin_access_identity_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        for response in self.execute(
            self.client.create_cloud_front_origin_access_identity,
            "CloudFrontOriginAccessIdentity",
            filters_req=request_dict,
        ):
            return response

    def create_invalidation(self, distribution, paths):
        """
        Standard.

        :param distribution:
        :param paths:
        :return:
        """

        self.create_invalidation_raw(distribution.generate_create_invalidation(paths))

    def create_invalidation_raw(self, request):
        """
        Standard.

        :param request:
        :return:
        """

        for response in self.execute(
            self.client.create_invalidation, "Invalidation", filters_req=request
        ):
            return response

    def get_distribution_config(self, distribution_id):
        response = self.client.get_distribution_config(
            Id=distribution_id
        )
        return response
