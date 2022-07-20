"""
AWS lambda client to handle lambda service API requests.
"""
import pdb

import time

from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.application_auto_scaling_policy import ApplicationAutoScalingPolicy
from horey.aws_api.aws_services_entities.application_auto_scaling_scalable_target import ApplicationAutoScalingScalableTarget


from horey.h_logger import get_logger
logger = get_logger()


class ApplicationAutoScalingClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "application-autoscaling"
        super().__init__(client_name)
        pdb.set_trace()

    def get_all_policies(self, region=None):
        """
        Get all policies in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_policies(region)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_policies(region)

        return final_result

    def get_region_policies(self, region, custom_filter=None):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.describe_scaling_policies, "ScalingPolicies", filters_req=custom_filter):
            obj = ApplicationAutoScalingPolicy(dict_src)
            final_result.append(obj)

        return final_result

    def provision_policy(self, autoscaling_policy):
        pdb.set_trace()
        AWSAccount.set_aws_region(autoscaling_policy.region)
        response = self.provision_policy_raw(autoscaling_policy.generate_create_request())
        autoscaling_policy.update_from_raw_response(response)

    def provision_policy_raw(self, request_dict):
        pdb.set_trace()
        logger.info(f"Creating Auto Scaling Policy: {request_dict}")
        for response in self.execute(self.client.put_scaling_policy, None, raw_data=True, filters_req=request_dict):
            del response["ResponseMetadata"]
            return response

    def update_policy_information(self, policy):
        pdb.set_trace()
        AWSAccount.set_aws_region(policy.region)
        try:
            dict_src = self.execute_with_single_reply(self.client.describe_policies,
                                                       "ScalingPolicies",
                                                       filters_req={"PolicyNames":[policy.name]})
        except self.ZeroValuesException:
            return False
        policy.update_from_raw_response(dict_src)
        return True

        ret = list(self.execute(self.client.describe_scalable_targets, "ScalableTargets", filters_req=custom_filter))# endregion

    def get_all_scalable_targets(self, region=None):
        """
        Get all scalable_targets in all regions.
        :return:
        """
        pdb.set_trace()
        if region is not None:
            return self.get_region_scalable_targets(region)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_scalable_targets(region)

        return final_result

    def get_region_scalable_targets(self, region, custom_filter=None):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.describe_scalable_targets, "ScalableTargets", filters_req=custom_filter):
            obj = ApplicationAutoScalingScalableTarget(dict_src)
            final_result.append(obj)

        return final_result

    def provision_scalable_target(self, autoscaling_scalable_target):
        pdb.set_trace()
        AWSAccount.set_aws_region(autoscaling_scalable_target.region)
        response = self.provision_scalable_target_raw(autoscaling_scalable_target.generate_create_request())
        autoscaling_scalable_target.update_from_raw_response(response)

    def provision_scalable_target_raw(self, request_dict):
        pdb.set_trace()
        logger.info(f"Creating Auto Scaling Policy: {request_dict}")
        for response in self.execute(self.client.put_scaling_scalable_target, None, raw_data=True, filters_req=request_dict):
            del response["ResponseMetadata"]
            return response

    def update_scalable_target_information(self, scalable_target):
        pdb.set_trace()
        AWSAccount.set_aws_region(scalable_target.region)
        try:
            dict_src = self.execute_with_single_reply(self.client.describe_scalable_targets,
                                                       "ScalingPolicies",
                                                       filters_req={"PolicyNames":[scalable_target.name]})
        except self.ZeroValuesException:
            return False
        scalable_target.update_from_raw_response(dict_src)
        return True

