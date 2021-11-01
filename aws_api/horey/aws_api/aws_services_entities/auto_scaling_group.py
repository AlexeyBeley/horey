"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region
from enum import Enum

class AutoScalingGroup(AwsObject):
    """
    AWS AutoScalingGroup class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None
        self.status = None
        self.availability_zones = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "AutoScalingGroupName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "AutoScalingGroupARN": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
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
        }

        self.init_attrs(dict_src, init_options)

    def _init_object_from_cache(self, dict_src):
        """
        Init from cache
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def update_from_raw_response(self, dict_src):
        init_options = {
            "AutoScalingGroupName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "AutoScalingGroupARN": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
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
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        request = dict()
        request["AutoScalingGroupName"] = self.name
        request["LaunchTemplate"] = self.launch_template
        request["MinSize"] = self.min_size
        request["MaxSize"] = self.max_size
        request["Tags"] = [
                   {
                       "ResourceType": "auto-scaling-group",
                       "Key": tag["Key"],
                       "Value": tag["Value"],
                       "PropagateAtLaunch": True
                   } for tag in self.tags
               ]
        request["ServiceLinkedRoleARN"] = self.service_linked_role_arn
        request["DesiredCapacity"] = self.desired_capacity
        request["DefaultCooldown"] = self.default_cooldown
        if self.availability_zones is not None:
            request["AvailabilityZones"] = self.availability_zones
        request["HealthCheckType"] = self.health_check_type
        request["HealthCheckGracePeriod"] = self.health_check_grace_period
        request["VPCZoneIdentifier"] = self.vpc_zone_identifier
        request["TerminationPolicies"] = self.termination_policies
        request["NewInstancesProtectedFromScaleIn"] = self.new_instances_protected_from_scale_in
        return request

    def generate_dispose_request(self):
        request = dict()
        request["AutoScalingGroupName"] = self.name
        request["ForceDelete"] = True
        return request

    @property
    def region(self):
        if self._region is not None:
            return self._region

        raise NotImplementedError()
        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value

    def get_status(self):
        if self.status is None:
            return self.Status.ACTIVE
        elif self.status == "Delete in progress":
            return self.Status.DELETING
        else:
            raise NotImplementedError(self.status)

    class Status(Enum):
        ACTIVE = 0
        DELETING = 1
