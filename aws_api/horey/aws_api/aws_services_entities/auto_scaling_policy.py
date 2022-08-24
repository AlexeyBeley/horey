"""
AWS AutoScalingPolicy representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class AutoScalingPolicy(AwsObject):
    """
    AWS AutoScalingPolicy class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None
        self.target_tracking_configuration = None
        self.arn = None

        self.auto_scaling_group_name = None
        self.policy_type = None
        self.adjustment_type = None

        self.scaling_adjustment = None
        self.cooldown = None
        self.enabled = None
        self.max_size = None

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
        """
        Response from server.

        @param dict_src:
        @return:
        """
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
        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard

        @return:
        """
        request = {"AutoScalingGroupName": self.auto_scaling_group_name,
                   "PolicyName": self.name,
                   "PolicyType": self.policy_type,
                   "AdjustmentType": self.adjustment_type,
                   "ScalingAdjustment": self.scaling_adjustment,
                   "Cooldown": self.cooldown,
                   "Enabled": self.enabled}

        if self.target_tracking_configuration is not None:
            request["TargetTrackingConfiguration"] = self.target_tracking_configuration

        return request

    def generate_update_request(self, desired_state):
        """
        Standard.

        @param desired_state:
        @return:
        """
        request = {}

        if self.max_size != desired_state.max_size:
            request["AutoScalingPolicyName"] = desired_state.name
            request["MaxSize"] = desired_state.max_size

        return request if request else None

    def generate_dispose_request(self):
        """
        Standard

        @return:
        """
        request = {"AutoScalingPolicyName": self.name, "ForceDelete": True}
        return request

    @property
    def region(self):
        """
        Self region

        @return:
        """
        if self._region is not None:
            return self._region

        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        """
        Region setter.

        @param value:
        @return:
        """
        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value
