"""
AWS lambda client to handle lambda service API requests.
"""

from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.application_auto_scaling_policy import (
    ApplicationAutoScalingPolicy,
)
from horey.aws_api.aws_services_entities.application_auto_scaling_scalable_target import (
    ApplicationAutoScalingScalableTarget,
)

from horey.h_logger import get_logger

logger = get_logger()


class ApplicationAutoScalingClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "application-autoscaling"
        super().__init__(client_name)
        self.service_namespaces = ["ecs"]

    # pylint: disable= too-many-arguments
    def yield_policies(self, region=None, update_info=False, filters_req=None):
        """
        Yield policies

        :return:
        """

        regional_fetcher_generator = self.yield_policies_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            ApplicationAutoScalingPolicy,
                                                            update_info=update_info,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_policies_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        filters_req = filters_req or {}

        if filters_req.get("ServiceNamespace"):
            namespaces = [filters_req.get("ServiceNamespace")]
        else:
            namespaces = self.service_namespaces

        for namespace in namespaces:
            filters_req["ServiceNamespace"] = namespace
            yield from self.execute(
                    self.get_session_client(region=region).describe_scaling_policies, "ScalingPolicies", filters_req=filters_req
            )

    def get_all_policies(self, region=None):
        """
        Get all policies in all regions.
                if region is not None:
            return self.get_region_policies(region)

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_policies(_region)

        return final_result

        :return:
        """

        return list(self.yield_policies(region=region))

    def get_region_policies(self, region, custom_filter=None):
        """
        Standard.
        if custom_filter is not None and "ServiceNamespace" in custom_filter:
            return self.get_region_policies_raw(region, custom_filter)

        final_result = []
        custom_filter = custom_filter if custom_filter is not None else {}
        for service_namespace in self.service_namespaces:
            custom_filter["ServiceNamespace"] = service_namespace
            final_result += self.get_region_policies_raw(region, custom_filter)

        return final_result
        :param region:
        :param custom_filter:
        :return:
        """

        return list(self.yield_policies(region=region))

    def get_region_policies_raw(self, region, dict_request):
        """
        Standard.

        :param dict_request:
        :return:
        """

        final_result = []
        for dict_src in self.execute(
                self.get_session_client(region=region).describe_scaling_policies,
                "ScalingPolicies",
                filters_req=dict_request,
        ):
            obj = ApplicationAutoScalingPolicy(dict_src)
            final_result.append(obj)

        return final_result

    def provision_policy(self, autoscaling_policy):
        """
        Standard.

        :param autoscaling_policy:
        :return:
        """

        response = self.provision_policy_raw(autoscaling_policy.region,
                                             autoscaling_policy.generate_create_request()
                                             )
        autoscaling_policy.update_from_raw_response(response)

    def provision_policy_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """
        logger.info(f"Creating Auto Scaling Policy: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).put_scaling_policy,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            del response["ResponseMetadata"]
            return response

    def update_policy_information(self, policy):
        """
        Standard.

        :param policy:
        :return:
        """

        try:
            dict_src = self.execute_with_single_reply(
                self.get_session_client(region=policy.region).describe_scaling_policies,
                "ScalingPolicies",
                filters_req={
                    "ServiceNamespace": policy.service_namespace,
                    "PolicyNames": [policy.name],
                },
            )
        except self.ZeroValuesException:
            return False
        policy.update_from_raw_response(dict_src)
        return True

    def get_all_scalable_targets(self, region=None):
        """
        Get all scalable_targets in all regions.
        :return:
        """
        if region is not None:
            return self.get_region_scalable_targets(region)

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_scalable_targets(_region)

        return final_result

    def get_region_scalable_targets(self, region, custom_filter=None):
        """
        Standard.

        :param region:
        :param custom_filter:
        :return:
        """

        if custom_filter is not None and "ServiceNamespace" in custom_filter:
            return self.get_region_scalable_targets_raw(region, custom_filter)

        final_result = []
        custom_filter = custom_filter if custom_filter is not None else {}
        for service_namespace in self.service_namespaces:
            custom_filter["ServiceNamespace"] = service_namespace
            final_result += self.get_region_scalable_targets_raw(region, custom_filter)

        return final_result

    def get_region_scalable_targets_raw(self, region, dict_request):
        """
        Standard.

        :param dict_request:
        :return:
        """

        final_result = []
        for dict_src in self.execute(
                self.get_session_client(region=region).describe_scalable_targets,
                "ScalableTargets",
                filters_req=dict_request,
        ):
            obj = ApplicationAutoScalingScalableTarget(dict_src)
            final_result.append(obj)

        return final_result

    def provision_scalable_target(self, autoscaling_scalable_target):
        """
        Standard.

        :param autoscaling_scalable_target:
        :return:
        """

        self.provision_scalable_target_raw(autoscaling_scalable_target.region,
                                           autoscaling_scalable_target.generate_create_request()
                                           )

    def provision_scalable_target_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Registering Auto Scaling scalable target: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).register_scalable_target,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            return response

    def update_scalable_target_information(self, scalable_target):
        """
        Standard.

        :param scalable_target:
        :return:
        """
        try:
            dict_src = self.execute_with_single_reply(
                self.get_session_client(region=scalable_target.region).describe_scalable_targets,
                "ScalingPolicies",
                filters_req={"PolicyNames": [scalable_target.name]},
            )
        except self.ZeroValuesException:
            return False
        scalable_target.update_from_raw_response(dict_src)
        return True
