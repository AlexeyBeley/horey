"""
AWS lambda client to handle lambda service API requests.
"""
import pdb
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.auto_scaling_group import AutoScalingGroup

from horey.h_logger import get_logger
logger = get_logger()


class AutoScalingClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "autoscaling"
        super().__init__(client_name)

    def get_all_auto_scaling_groups(self, region=None):
        """
        Get all auto_scaling_groups in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_auto_scaling_groups(region)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_auto_scaling_groups(region)

        return final_result

    def get_region_auto_scaling_groups(self, region):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.describe_auto_scaling_groups, "AutoScalingGroups"):
            obj = AutoScalingGroup(dict_src)
            final_result.append(obj)

        return final_result

    def provision_auto_scaling_group(self, autoscaling_group):
        region_objects = self.get_region_auto_scaling_groups(autoscaling_group.region)
        for region_object in region_objects:
            if region_object.name == autoscaling_group.name:
                autoscaling_group.update_from_raw_response(region_object.dict_src)
                return

        AWSAccount.set_aws_region(autoscaling_group.region)
        response = self.provision_auto_scaling_group_raw(autoscaling_group.generate_create_request())
        autoscaling_group.update_from_raw_create(response)

    def provision_auto_scaling_group_raw(self, request_dict):
        logger.info(f"Creating Auto Scaling Group: {request_dict}")
        for response in self.execute(self.client.create_auto_scaling_group, "ResponseMetadata", raw_data=True, filters_req=request_dict):
            pdb.set_trace()
            return response
