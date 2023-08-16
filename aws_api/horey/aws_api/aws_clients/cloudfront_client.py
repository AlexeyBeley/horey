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
from horey.aws_api.aws_services_entities.cloudfront_function import (
    CloudfrontFunction,
)
from horey.aws_api.aws_services_entities.cloudfront_response_headers_policy import (
    CloudfrontResponseHeadersPolicy,
)
from horey.aws_api.base_entities.aws_account import AWSAccount
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

    def get_all_functions(self, full_information=False):
        """
        Get the full list

        :param full_information:
        :return:
        """

        lst_ret = []
        for ret in self.execute(self.client.list_functions, "FunctionList"):
            for dict_item in ret["Items"]:
                function = CloudfrontFunction(dict_item)
                lst_ret.append(function)
                if full_information:
                    self.update_function_full_information(function)
        return lst_ret

    def update_function_full_information(self, function):
        """
        Get the code.

        :param function:
        :return:
        """
        if function.region:
            AWSAccount.set_aws_region(function.region)

        for response in self.execute(self.client.get_function, None, raw_data=True, filters_req={"Name": function.name}):
            del response["ResponseMetadata"]
            response["FunctionCode"] = response["FunctionCode"].read().decode("utf-8")
            function.update_from_raw_response(response)

    def update_function_info(self, function: CloudfrontFunction, full_information=False):
        """
        Standard.

        :param function:
        :return:
        """

        if function.region:
            AWSAccount.set_aws_region(function.region)

        filters_req = {"Name": function.name}

        if function.stage:
            filters_req["Stage"] = function.stage
        else:
            filters_req["Stage"] = "LIVE"

        for response in self.execute(self.client.describe_function, None, raw_data=True,
                                     filters_req=filters_req, exception_ignore_callback=lambda exception_inst: "NoSuchFunctionExists" in repr(exception_inst)):
            function.update_from_raw_response(response)
            break
        else:
            return False

        if full_information:
            self.update_function_full_information(function)

        return  True

    def provision_function(self, function: CloudfrontFunction):
        """
        Standard.

        :param function:
        :return:
        """

        function_current = CloudfrontFunction({})
        function_current.region = function.region
        function_current.name = function.name
        function_current.stage = function.stage if function.stage else "LIVE"

        AWSAccount.set_aws_region(function.region)
        if not self.update_function_info(function_current, full_information=True):
            response = self.provision_function_raw(function.generate_create_request())
            if function.stage == "LIVE":
                function.update_from_raw_response(response)
                response = self.publish_function_raw(function.generate_publish_request())
            function.update_from_raw_response(response)
            return None

        request = function_current.generate_update_request(function)
        if request:
            response = self.update_function_raw(request)
            function.update_from_raw_response(response)
            if function.stage == "LIVE":
                response = self.publish_function_raw(function.generate_publish_request())
                function.update_from_raw_response(response)

        return self.update_function_info(function)

    def provision_function_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Creating cloudfornt function {request_dict}")

        for response in self.execute(
            self.client.create_function,
            None,
            raw_data=True,
            filters_req=request_dict,
        ):
            return response

    def publish_function_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Publishing cloudfornt function {request_dict}")

        for response in self.execute(
            self.client.publish_function,
            None,
            raw_data=True,
            filters_req=request_dict,
        ):
            return response

    def update_function_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Updating cloudfornt function {request_dict}")

        for response in self.execute(
            self.client.update_function,
            None,
            raw_data=True,
            filters_req=request_dict,
        ):
            return response

    def dispose_function(self, function):
        """
        Standard.

        :param function:
        :return:
        """

        AWSAccount.set_aws_region(function.region)
        if self.update_function_info(function, full_information=False):
            self.dispose_function_raw(function.generate_dispose_request())

    def dispose_function_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Deleting cloudfornt function{request_dict}")
        for response in self.execute(
                self.client.delete_function,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            return response

    def test_function(self, function: CloudfrontFunction, event_object):
        """
        Test the function

        :param function:
        :param event_object:
        :return:
        """

        request = function.generate_test_request(event_object)
        response = self.test_function_raw(request)
        return response

    def test_function_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Testing cloudfornt function{request_dict}")
        for response in self.execute(
                self.client.test_function,
                "TestResult",
                filters_req=request_dict, instant_raise=True
        ):
            return response

    def get_all_response_headers_policies(self, full_information=True):
        """
        Docstring standard.

        :return:
        """

        final_result = []

        for response in self.execute(
            self.client.list_response_headers_policies,
            "ResponseHeadersPolicyList",
            internal_starting_token=True,
        ):
            for dict_src in response["Items"]:
                pol = CloudfrontResponseHeadersPolicy(dict_src)
                final_result.append(pol)
                if full_information:
                    self.update_response_headers_policy_full_information(pol)

        return final_result

    def update_response_headers_policy_full_information(self, policy: CloudfrontResponseHeadersPolicy):
        """
        Standard.

        :param policy:
        :return:
        """

        for response in self.execute(
            self.client.get_response_headers_policy,
            None, raw_data=True, filters_req={"Id": policy.id}
        ):

            policy.update_from_raw_response(response)

    def update_response_headers_policy_info(self, policy: CloudfrontResponseHeadersPolicy, full_information=False):
        """
        Standard

        :param policy:
        :param full_information:
        :return:
        """

        if policy.id is None:
            for current_policy in self.get_all_response_headers_policies(full_information=False):
                if current_policy.name == policy.name:
                    policy.update_from_raw_response(current_policy.dict_src)
                    break
            else:
                return False

        if full_information:
            self.update_response_headers_policy_full_information(policy)

        return True

    def provision_response_headers_policy(self, desired_policy: CloudfrontResponseHeadersPolicy):
        """
        Standard.

        :param desired_policy:
        :return:
        """

        current_policy = CloudfrontResponseHeadersPolicy({})
        current_policy.name = desired_policy.name
        if not self.update_response_headers_policy_info(current_policy, full_information=True):
            response = self.provision_response_headers_policy_raw(desired_policy.generate_create_request())
            desired_policy.update_from_raw_response(response)
            return

        update_request = current_policy.generate_update_request(desired_policy)
        if update_request:
            response = self.update_response_headers_policy_raw(update_request)
            desired_policy.update_from_raw_response(response)

        self.update_response_headers_policy_info(desired_policy, full_information=True)

    def provision_response_headers_policy_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """
        logger.info(f"Creating response_headers_policy {request_dict}")
        for response in self.execute(
                self.client.create_response_headers_policy,
                "ResponseHeadersPolicy",
                filters_req=request_dict, instant_raise=True
        ):
            return response

    def update_response_headers_policy_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Updating response_headers_policy {request_dict}")
        for response in self.execute(
                self.client.update_response_headers_policy,
                "ResponseHeadersPolicy",
                filters_req=request_dict
        ):
            return response

    def dispose_response_headers_policy(self, policy: CloudfrontResponseHeadersPolicy):
        """
        Standard.

        :param policy:
        :return:
        """
        if self.update_response_headers_policy_info(policy, full_information=True):
            self.dispose_response_headers_policy_raw(policy.generate_dispose_request())

    def dispose_response_headers_policy_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Deleting response_headers_policy {request_dict}")
        for response in self.execute(
                self.client.delete_response_headers_policy,
                None,
                raw_data=True,
                filters_req=request_dict
        ):
            return response
