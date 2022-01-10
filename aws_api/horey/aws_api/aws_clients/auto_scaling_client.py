"""
AWS lambda client to handle lambda service API requests.
"""
import pdb

import time

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

    def get_region_auto_scaling_groups(self, region, names=None):
        final_result = list()
        filters_req = dict()
        if names is not None:
            filters_req["AutoScalingGroupNames"] = names
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.describe_auto_scaling_groups, "AutoScalingGroups", filters_req=filters_req):
            obj = AutoScalingGroup(dict_src)
            final_result.append(obj)

        return final_result

    def provision_auto_scaling_group(self, autoscaling_group: AutoScalingGroup):
        region_objects = self.get_region_auto_scaling_groups(autoscaling_group.region, names=[autoscaling_group.name])
        sleep_time = 5
        retries_count = 300//sleep_time

        retry_counter = 0
        while len(region_objects) > 0 and region_objects[0].get_status() == autoscaling_group.Status.DELETING:
            retry_counter += 1
            if retry_counter > retries_count:
                raise TimeoutError(f"{autoscaling_group.name} deletion takes more then 300 sec")

            logger.info(f"{autoscaling_group.name} is being deleted. Going to sleep for {sleep_time} seconds")
            time.sleep(sleep_time)
            region_objects = self.get_region_auto_scaling_groups(autoscaling_group.region,
                                                                     names=[autoscaling_group.name])

        if len(region_objects) > 0:
            update_request = region_objects[0].generate_update_request(autoscaling_group)
            if update_request is not None:
                self.update_auto_scaling_group_raw(update_request)
                for _ in range(retries_count):
                    region_objects = self.get_region_auto_scaling_groups(autoscaling_group.region, names=[autoscaling_group.name])
                    if len(region_objects[0].max_size) == autoscaling_group.max_size:
                        break
                    logger.info(f"Waiting for auto scaling group max_size change from "
                                f"{len(region_objects[0].max_size)} to {autoscaling_group.max_size}")
                    time.sleep(sleep_time)
                else:
                    raise RuntimeError(f"Failed to change auto scaling group '{autoscaling_group.name}' "
                                       f"max_size to {autoscaling_group.max_size}")

            if autoscaling_group.desired_capacity != region_objects[0].desired_capacity:
                self.set_desired_capacity_raw(autoscaling_group.generate_desired_capacity_request())

                for _ in range(retries_count):
                    region_objects = self.get_region_auto_scaling_groups(autoscaling_group.region, names=[autoscaling_group.name])
                    if len(region_objects[0].instances) == autoscaling_group.desired_capacity:
                        break
                    logger.info(f"Waiting for auto scaling group desired capacity change from "
                                f"{len(region_objects[0].instances)} to {autoscaling_group.desired_capacity}")
                    time.sleep(sleep_time)
                else:
                    raise RuntimeError(f"Failed to change auto scaling group '{autoscaling_group.name}' "
                                       f"desired capacity to {autoscaling_group.desired_capacity}")

            autoscaling_group.update_from_raw_response(region_objects[0].dict_src)
            return

        # creation
        AWSAccount.set_aws_region(autoscaling_group.region)
        self.provision_auto_scaling_group_raw(autoscaling_group.generate_create_request())

        # update arn
        region_objects = self.get_region_auto_scaling_groups(autoscaling_group.region, names=[autoscaling_group.name])

        sleep_time = 2
        retries_count = 300/sleep_time
        retry_counter = 0
        while len(region_objects) == 0:
            retry_counter += 1
            if retry_counter > retries_count:
                raise TimeoutError(f"{autoscaling_group.name} creation takes more then 300 sec")
            logger.info(f"{autoscaling_group.name} is being created. Going to sleep for {sleep_time} seconds")
            time.sleep(sleep_time)
            region_objects = self.get_region_auto_scaling_groups(autoscaling_group.region,
                                                             names=[autoscaling_group.name])

        autoscaling_group.update_from_raw_response(region_objects[0].dict_src)

    def set_desired_capacity_raw(self, request_dict):
        logger.info(f"Modifying Scaling Group: {request_dict}")
        for response in self.execute(self.client.set_desired_capacity, None, raw_data=True, filters_req=request_dict):
            return response

    def update_auto_scaling_group_raw(self, request_dict):
        pdb.set_trace()
        logger.info(f"Modifying Auto Scaling Group: {request_dict}")
        for response in self.execute(self.client.update_auto_scaling_group, None, raw_data=True, filters_req=request_dict):
            return response

    def provision_auto_scaling_group_raw(self, request_dict):
        logger.info(f"Creating Auto Scaling Group: {request_dict}")
        for response in self.execute(self.client.create_auto_scaling_group, "ResponseMetadata", raw_data=True, filters_req=request_dict):
            return response

    def dispose_auto_scaling_group(self, autoscaling_group):
        AWSAccount.set_aws_region(autoscaling_group.region)
        self.dispose_auto_scaling_group_raw(autoscaling_group.generate_dispose_request())

    def dispose_auto_scaling_group_raw(self, request_dict):
        logger.info(f"Disposing Auto Scaling Group: {request_dict}")
        for response in self.execute(self.client.delete_auto_scaling_group, None, raw_data=True, filters_req=request_dict):
            return response
