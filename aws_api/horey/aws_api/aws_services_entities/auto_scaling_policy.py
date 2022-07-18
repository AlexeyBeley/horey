"""
AWS AutoScalingPolicy representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class AutoScalingPolicy(AwsObject):
    """
    AWS AutoScalingPolicy class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "PolicyName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "PolicyARN": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "AutoScalingGroupName": self.init_default_attr,
            "PolicyType": self.init_default_attr,
            "StepAdjustments": self.init_default_attr,
            "EstimatedInstanceWarmup": self.init_default_attr,
            "Alarms": self.init_default_attr,
            "TargetTrackingConfiguration": self.init_default_attr,
            "Enabled": self.init_default_attr,
            "AdjustmentType": self.init_default_attr,
            "ScalingAdjustment": self.init_default_attr,
            "Cooldown": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options, raise_on_no_option=True)

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
            "PolicyName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "PolicyARN": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "AutoScalingGroupName": self.init_default_attr,
            "PolicyType": self.init_default_attr,
            "StepAdjustments": self.init_default_attr,
            "EstimatedInstanceWarmup": self.init_default_attr,
            "Alarms": self.init_default_attr,
            "TargetTrackingConfiguration": self.init_default_attr,
            "Enabled": self.init_default_attr,
            "AdjustmentType": self.init_default_attr,
            "ScalingAdjustment": self.init_default_attr,
            "Cooldown": self.init_default_attr,
        }
        pdb.set_trace()
        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        request = dict()
        request["AutoScalingGroupName"] = self.auto_scaling_group_name
        request["PolicyName"] = self.name

        request["PolicyType"] = self.policy_type
        request["AdjustmentType"] = self.adjustment_type

        request["ScalingAdjustment"] = self.scaling_adjustment
        request["Cooldown"] = self.cooldown
        request["Alarms"] = self.alarms
        request["Enabled"] = self.enabled
        return request

    def generate_update_request(self, desired_state):
        pdb.set_trace()
        request = dict()

        if self.max_size != desired_state.max_size:
            request["AutoScalingPolicyName"] = desired_state.name
            request["MaxSize"] = desired_state.max_size

        return request if request else None

    def generate_dispose_request(self):
        pdb.set_trace()
        request = dict()
        request["AutoScalingPolicyName"] = self.name
        request["ForceDelete"] = True
        return request

    @property
    def region(self):
        if self._region is not None:
            return self._region

        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value
