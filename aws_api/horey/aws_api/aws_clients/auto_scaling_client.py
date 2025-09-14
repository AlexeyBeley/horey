"""
AWS lambda client to handle lambda service API requests.
"""

import time

from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.auto_scaling_group import AutoScalingGroup
from horey.aws_api.aws_services_entities.auto_scaling_policy import AutoScalingPolicy
from horey.aws_api.aws_services_entities.auto_scaling_activity import AutoScalingActivity

from horey.h_logger import get_logger

logger = get_logger()


class AutoScalingClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "autoscaling"
        super().__init__(client_name)
    
    def yield_auto_scaling_groups(self, region=None, update_info=False, filters_req=None):
        """
        Yield tables

        :return:
        """

        regional_fetcher_generator = self.yield_auto_scaling_groups_raw

        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            AutoScalingGroup,
                                                            update_info=update_info,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_auto_scaling_groups_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
            self.get_session_client(region=region).describe_auto_scaling_groups, "AutoScalingGroups", filters_req=filters_req
        )

    def get_all_auto_scaling_groups(self, region=None):
        """
        Get all auto_scaling_groups in all regions.
        :return:
        """

        return list(self.yield_auto_scaling_groups(region=region))

    def get_region_auto_scaling_groups(self, region, names=None):
        """
        Standard.

        :param region:
        :param names:
        :return:
        """

        filters_req = {"AutoScalingGroupNames": names}

        return list(self.yield_auto_scaling_groups(region=region, filters_req=filters_req))

    # pylint: disable = too-many-branches
    def provision_auto_scaling_group(self, autoscaling_group: AutoScalingGroup):
        """
        Provision - add or update autoscaling group.

        :param autoscaling_group:
        :return:
        """
        for attr in ["region", "name"]:
            if not getattr(autoscaling_group, attr):
                raise ValueError(f"'{attr}' must be set")

        region_objects = self.get_region_auto_scaling_groups(
            autoscaling_group.region, names=[autoscaling_group.name]
        )
        sleep_time = 5
        retries_count = 300 // sleep_time

        retry_counter = 0
        while (
                len(region_objects) > 0
                and region_objects[0].get_status() == autoscaling_group.Status.DELETING
        ):
            retry_counter += 1
            if retry_counter > retries_count:
                raise TimeoutError(
                    f"{autoscaling_group.name} deletion takes more then 300 sec"
                )

            logger.info(
                f"{autoscaling_group.name} is being deleted. Going to sleep for {sleep_time} seconds"
            )
            time.sleep(sleep_time)
            region_objects = self.get_region_auto_scaling_groups(
                autoscaling_group.region, names=[autoscaling_group.name]
            )
        if len(region_objects) > 1:
            raise RuntimeError(
                f"{autoscaling_group.name} found > 1: {len(region_objects)}"
            )

        if len(region_objects) > 0:
            update_request = region_objects[0].generate_update_request(
                autoscaling_group
            )
            if update_request is not None:
                self.update_auto_scaling_group_raw(autoscaling_group.region, update_request)
                for _ in range(retries_count):
                    region_objects = self.get_region_auto_scaling_groups(
                        autoscaling_group.region, names=[autoscaling_group.name]
                    )
                    if region_objects[0].max_size == autoscaling_group.max_size and \
                            region_objects[0].min_size == autoscaling_group.min_size:
                        break
                    logger.info(
                        f"Waiting for auto scaling group max_size/min_size change from "
                        f"{region_objects[0].max_size}/{region_objects[0].min_size} to"
                        f" {autoscaling_group.max_size}/{autoscaling_group.min_size}"
                    )
                    time.sleep(sleep_time)
                else:
                    raise RuntimeError(
                        f"Failed to change auto scaling group '{autoscaling_group.name}' "
                        f"max_size to {autoscaling_group.max_size}"
                    )

            if autoscaling_group.desired_capacity != region_objects[0].desired_capacity:
                self.set_desired_capacity_raw(autoscaling_group.region,
                                              autoscaling_group.generate_desired_capacity_request()
                                              )

                for _ in range(retries_count):
                    region_objects = self.get_region_auto_scaling_groups(
                        autoscaling_group.region, names=[autoscaling_group.name]
                    )
                    if (
                            len(region_objects[0].instances)
                            == autoscaling_group.desired_capacity
                    ):
                        break
                    logger.info(
                        f"Waiting for auto scaling group desired capacity change from "
                        f"{len(region_objects[0].instances)} to {autoscaling_group.desired_capacity}"
                    )
                    time.sleep(sleep_time)
                else:
                    raise RuntimeError(
                        f"Failed to change auto scaling group '{autoscaling_group.name}' "
                        f"desired capacity to {autoscaling_group.desired_capacity}"
                    )

            autoscaling_group.update_from_raw_response(region_objects[0].dict_src)
            return

        # creation
        self.provision_auto_scaling_group_raw(autoscaling_group.region,
                                              autoscaling_group.generate_create_request()
                                              )

        # update arn
        region_objects = self.get_region_auto_scaling_groups(
            autoscaling_group.region, names=[autoscaling_group.name]
        )

        sleep_time = 2
        retries_count = 300 / sleep_time
        retry_counter = 0
        while len(region_objects) == 0:
            retry_counter += 1
            if retry_counter > retries_count:
                raise TimeoutError(
                    f"{autoscaling_group.name} creation takes more then 300 sec"
                )
            logger.info(
                f"{autoscaling_group.name} is being created. Going to sleep for {sleep_time} seconds"
            )
            time.sleep(sleep_time)
            region_objects = self.get_region_auto_scaling_groups(
                autoscaling_group.region, names=[autoscaling_group.name]
            )

        autoscaling_group.update_from_raw_response(region_objects[0].dict_src)

    def set_desired_capacity_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Modifying Scaling Group: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).set_desired_capacity,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            return response

    def update_auto_scaling_group_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Modifying Auto Scaling Group: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).update_auto_scaling_group,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            return response

    def provision_auto_scaling_group_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Creating Auto Scaling Group: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_auto_scaling_group,
                "ResponseMetadata",
                raw_data=True,
                filters_req=request_dict,
        ):
            return response

    def dispose_auto_scaling_group(self, autoscaling_group):
        """
        Standard.

        :param autoscaling_group:
        :return:
        """

        self.dispose_auto_scaling_group_raw(autoscaling_group.region,
                                            autoscaling_group.generate_dispose_request()
                                            )

    def dispose_auto_scaling_group_raw(self, region, request_dict):
        """
        Standard.

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Disposing Auto Scaling Group: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).delete_auto_scaling_group,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            self.clear_cache(AutoScalingGroup)
            return response

    def get_all_policies(self, region=None):
        """
        Get all policies in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_policies(region)

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_policies(_region)

        return final_result

    def get_region_policies(self, region, custom_filter=None):
        """
        Standard.

        :param region:
        :param custom_filter:
        :return:
        """

        final_result = []
        for dict_src in self.execute(
                self.get_session_client(region=region).describe_policies, "ScalingPolicies", filters_req=custom_filter
        ):
            obj = AutoScalingPolicy(dict_src)
            final_result.append(obj)

        return final_result

    def provision_policy(self, autoscaling_policy: AutoScalingPolicy):
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

    def update_policy_information(self, policy: AutoScalingPolicy):
        """
        Fetch policy information from AWS api.

        :param policy:
        :return:
        """
        filters_req = {"PolicyNames": [policy.name]}
        if policy.auto_scaling_group_name:
            filters_req["AutoScalingGroupName"] = policy.auto_scaling_group_name

        try:
            dict_src = self.execute_with_single_reply(
                self.get_session_client(region=policy.region).describe_policies,
                "ScalingPolicies",
                filters_req=filters_req
            )
        except self.ZeroValuesException:
            return False
        policy.update_from_raw_response(dict_src)
        return True

    def update_activity_information(self, activity: AutoScalingActivity):
        """
        Standard

        @param activity:
        @return:
        """
        filter_request = {"ActivityIds": [activity.id]}

        ret = list(response for response in self.execute(
            self.get_session_client(region=activity.region).describe_scaling_activities,
            "Activities",
            filters_req=filter_request))

        if len(ret) != 1:
            raise RuntimeError(f"Found {len(ret)=} != 1 items with params: {filter_request=}")

        activity.update_from_raw_response(ret[0])

    def detach_instances(self, auto_scaling_group, instance_ids, decrement=False):
        """
        Detach instances from asg.

        :param auto_scaling_group:
        :param instance_ids:
        :param decrement:
        :return:
        """

        request_dict = {"InstanceIds": instance_ids,
                        "AutoScalingGroupName": auto_scaling_group.name,
                        "ShouldDecrementDesiredCapacity": decrement}

        ret = self.detach_instances_raw(auto_scaling_group.region, request_dict)

        activity = AutoScalingActivity(ret)
        self.wait_for_status(activity,
                             self.update_activity_information,
                             [AutoScalingActivity.Status.SUCCESSFUL],
                             [AutoScalingActivity.Status.IN_PROGRESS],
                             [AutoScalingActivity.Status.FAILED],
                             )

        auto_scaling_group.desired_capacity -= len(instance_ids)

    def detach_instances_raw(self, region, request_dict):
        """
        Standard.

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Detaching instances from Auto Scaling group: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).detach_instances,
                "Activities",
                filters_req=request_dict,
        ):
            self.clear_cache(AutoScalingGroup)
            return response

    def update_auto_scaling_group_information(self, auto_scaling_group: AutoScalingGroup):
        """
        Standard.

        :param auto_scaling_group:
        :return:
        """

        if auto_scaling_group.name is None:
            auto_scaling_group.name = auto_scaling_group.arn.split("/")[-1]
        filters_req = {"AutoScalingGroupNames": [auto_scaling_group.name]}
        self.yield_auto_scaling_groups()
        ret = list(self.yield_auto_scaling_groups(region=auto_scaling_group.region, filters_req=filters_req))
        if not ret:
            return False

        if len(ret) != 1:
            raise RuntimeError(f"Can not find single auto scaling group by name: {auto_scaling_group.name}"
                               f" in region {auto_scaling_group.region.region_mark}")

        auto_scaling_group.update_from_attrs(ret[0])
        return True
