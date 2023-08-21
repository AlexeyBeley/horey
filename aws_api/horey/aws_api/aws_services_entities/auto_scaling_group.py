"""
AWS EC2 auto scaling group.
"""

from enum import Enum
from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class AutoScalingGroup(AwsObject):
    """
    AWS AutoScalingGroup class
    """
    # pylint: disable = too-many-instance-attributes

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None
        self.status = None
        self.availability_zones = None
        self.desired_capacity = None
        self.max_size = None
        self.min_size = None
        self.instances = None
        self.launch_template = None
        self.service_linked_role_arn = None
        self.default_cooldown = None
        self.health_check_type = None
        self.health_check_grace_period = None
        self.vpc_zone_identifier = None
        self.termination_policies = None
        self.new_instances_protected_from_scale_in = None
        self.arn = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        self.update_from_raw_response(dict_src)

    def _init_object_from_cache(self, dict_src):
        """
        Init from cache

        :param dict_src:
        :return:
        """

        options = {}
        self._init_from_cache(dict_src, options)

    def update_from_raw_response(self, dict_src):
        """
        Update instance from AWS server API raw response.

        :param dict_src:
        :return:
        """

        init_options = {
            "AutoScalingGroupName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "AutoScalingGroupARN": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
            "LaunchTemplate": self.init_default_attr,
            "MinSize": self.init_default_attr,
            "MaxSize": self.init_default_attr,
            "DesiredCapacity": self.init_default_attr,
            "DefaultCooldown": self.init_default_attr,
            "AvailabilityZones": self.init_default_attr,
            "LoadBalancerNames": self.init_default_attr,
            "TargetGroupARNs": self.init_default_attr,
            "HealthCheckType": self.init_default_attr,
            "HealthCheckGracePeriod": self.init_default_attr,
            "Instances": self.init_default_attr,
            "CreatedTime": self.init_default_attr,
            "SuspendedProcesses": self.init_default_attr,
            "VPCZoneIdentifier": self.init_default_attr,
            "EnabledMetrics": self.init_default_attr,
            "Tags": self.init_default_attr,
            "TerminationPolicies": self.init_default_attr,
            "NewInstancesProtectedFromScaleIn": self.init_default_attr,
            "ServiceLinkedRoleARN": self.init_default_attr,
            "LaunchConfigurationName": self.init_default_attr,
            "Status": self.init_default_attr,
            "CapacityRebalance": self.init_default_attr,
            "TrafficSources": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Generate create new scaling group request

        :return:
        """
        if self.tags is None:
            self.tags = []

        request = {"AutoScalingGroupName": self.name, "LaunchTemplate": self.launch_template, "MinSize": self.min_size,
                   "MaxSize": self.max_size, "Tags": [
                {
                    "ResourceType": "auto-scaling-group",
                    "Key": tag["Key"],
                    "Value": tag["Value"],
                    "PropagateAtLaunch": True,
                }
                for tag in self.tags
            ], "ServiceLinkedRoleARN": self.service_linked_role_arn, "DesiredCapacity": self.desired_capacity,
                   "DefaultCooldown": self.default_cooldown}

        if self.availability_zones is not None:
            request["AvailabilityZones"] = self.availability_zones
        request["HealthCheckType"] = self.health_check_type
        request["HealthCheckGracePeriod"] = self.health_check_grace_period
        request["VPCZoneIdentifier"] = self.vpc_zone_identifier
        request["TerminationPolicies"] = self.termination_policies
        request[
            "NewInstancesProtectedFromScaleIn"
        ] = self.new_instances_protected_from_scale_in
        return request

    def generate_update_request(self, desired_state):
        """
        Generate update request to change current status to desired.

        :param desired_state:
        :return:
        """

        for attr_name in ["max_size", "min_size"]:
            if getattr(self, attr_name) != getattr(desired_state, attr_name):
                request = {"AutoScalingGroupName": desired_state.name,
                           "MaxSize": desired_state.max_size,
                           "MinSize": desired_state.min_size}
                return request

        return None

    def generate_dispose_request(self):
        """
        Standard.

        :return:
        """

        request = {"AutoScalingGroupName": self.name, "ForceDelete": True}
        return request

    def generate_desired_capacity_request(self):
        """
        Generate changing desired capacity request.

        :return:
        """

        request = {"AutoScalingGroupName": self.name, "DesiredCapacity": self.desired_capacity}
        return request

    @property
    def region(self):
        """
        Self region.

        :return:
        """

        if self._region is not None:
            return self._region

        raise NotImplementedError()

    @region.setter
    def region(self, value):
        """
        Region setter.

        :param value:
        :return:
        """

        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value

    def get_status(self):
        """
        Get status Enum value

        :return:
        """

        if self.status is None:
            return self.Status.ACTIVE

        if self.status == "Delete in progress":
            return self.Status.DELETING

        raise NotImplementedError(self.status)

    class Status(Enum):
        """
        Possible statuses.

        """

        ACTIVE = 0
        DELETING = 1
