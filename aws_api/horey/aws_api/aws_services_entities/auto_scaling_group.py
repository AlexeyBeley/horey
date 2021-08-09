"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class AutoScalingGroup(AwsObject):
    """
    AWS AutoScalingGroup class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None

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

    def update_value_from_raw_response(self, raw_value):
        pdb.set_trace()
        raise NotImplementedError()

    def generate_create_request(self):
        request = dict()
        request["AutoScalingGroupName"] = self.name
        request["tags"] = self.tags
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
        request["AvailabilityZones"] = self.availability_zones
        request["HealthCheckType"] = self.health_check_type
        request["HealthCheckGracePeriod"] = self.health_check_grace_period
        request["VPCZoneIdentifier"] = self.vpc_zone_identifier
        request["TerminationPolicies"] = self.termination_policies
        request["NewInstancesProtectedFromScaleIn"] = self.new_instances_protected_from_scale_in
        return request

    def update_from_raw_create(self, dict_src):
        raise NotImplementedError()
        pdb.set_trace()
        init_options = {
            "ECSClusterId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "ECSClusterArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "AvailabilityZone": self.init_default_attr,
            "AvailabilityZoneId": self.init_default_attr,
            "AvailableIpAddressCount": self.init_default_attr,
            "CidrBlock": self.init_default_attr,
            "DefaultForAz": self.init_default_attr,
            "MapPublicIpOnLaunch": self.init_default_attr,
            "MapCustomerOwnedIpOnLaunch": self.init_default_attr,
            "State": self.init_default_attr,
            "VpcId": self.init_default_attr,
            "OwnerId": self.init_default_attr,
            "AssignIpv6AddressOnCreation": self.init_default_attr,
            "Ipv6CidrBlockAssociationSet": self.init_default_attr,
            "Tags": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    @property
    def region(self):
        raise NotImplementedError()
        if self._region is not None:
            return self._region

        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        raise NotImplementedError()
        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value

    def update_from_raw_response(self, dict_src):
        pdb.set_trace()