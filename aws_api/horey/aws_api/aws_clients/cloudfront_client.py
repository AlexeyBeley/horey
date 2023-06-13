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
        Get the full list

        :param full_information:
        :return:
        """
        return list(self.yield_all_distributions(full_information=full_information))

    def yield_all_distributions(self, full_information=True):
        """
        Yield over the cloudfront distributions

        :param full_information:
        :return:
        """

        for response in self.execute(
            self.client.list_distributions,
            "DistributionList",
            internal_starting_token=True,
        ):
            if response["Quantity"] == 0:
                continue

            for item in response["Items"]:
                obj = CloudfrontDistribution(item)

                if full_information:
                    for response_tags in self.execute(self.client.list_tags_for_resource, "Tags", filters_req={"Resource": obj.arn}):
                        obj.tags = response_tags["Items"]
                yield obj

    def provision_distribution(self, desired_distribution: CloudfrontDistribution):
        """
        WARNING! Comment is being used to identify distributions. If you've
        provisioned multiple cloudfront distributions with the same comment -
        it might raise an issue.

        @param desired_distribution:
        @return:
        """
        if desired_distribution.comment is None:
            raise ValueError("Comment is being used to identify cloudfront distributions. Comment was not set.")

        if not desired_distribution.get_tagname():
            raise ValueError("Cloudfront distribution tag name was not set.")

        existing_distribution = CloudfrontDistribution({})
        existing_distribution.tags = desired_distribution.tags
        existing_distribution.comment = desired_distribution.comment
        existing_distribution.distribution_config = desired_distribution.distribution_config
        self.update_distribution_information(existing_distribution)

        if existing_distribution.id is not None:
            request = existing_distribution.generate_update_request(desired_distribution)
            if request is not None:
                self.update_distribution_raw(request)

            self.update_distribution_information(desired_distribution)
            return

        response = self.provision_distribution_raw(
            desired_distribution.generate_create_request_with_tags()
        )

        desired_distribution.update_from_raw_response(response)

    def update_distribution_information(self, distribution: CloudfrontDistribution):
        """
        Get full information.

        :param distribution:
        :return:
        """
        try:
            distribution_aliases = distribution.distribution_config["Aliases"]["Items"]
        except KeyError:
            distribution_aliases = []

        for existing_distribution in self.yield_all_distributions():
            if existing_distribution.comment == distribution.comment:
                break
            if existing_distribution.get_tagname(ignore_missing_tag=True) == distribution.get_tagname():
                break

            for existing_distro_alias in existing_distribution.aliases["Items"]:
                if existing_distro_alias in distribution_aliases:
                    break
            else:
                continue
            break
        else:
            return

        distribution.update_from_raw_response(existing_distribution.dict_src)
        distribution.distribution_config = self.get_distribution_config_raw({"Id": distribution.id})

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

    def get_distribution_config_raw(self, request):
        """
        Get raw_data reply. Need for ETag param used by update_distribution.

        :param request:
        :return:
        """

        for response in self.execute(
                self.client.get_distribution_config, None, filters_req=request, raw_data=True
        ):
            return response
