"""
AWS ApplicationAutoScalingPolicy representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class ApplicationAutoScalingPolicy(AwsObject):
    """
    AWS ApplicationAutoScalingPolicy class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None
        self.target_tracking_configuration = None
        self.target_tracking_scaling_policy_configuration = None
        self.policy_type = None
        self.step_scaling_policy_configuration = None
        self.service_namespace = None
        self.arn = None
        self.resource_id = None
        self.scalable_dimension = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "PolicyName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "PolicyARN": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "ServiceNamespace": self.init_default_attr,
            "ResourceId": self.init_default_attr,
            "ScalableDimension": self.init_default_attr,
            "PolicyType": self.init_default_attr,
            "StepScalingPolicyConfiguration": self.init_default_attr,
            "Alarms": self.init_default_attr,
            "CreationTime": self.init_default_attr,
            "TargetTrackingScalingPolicyConfiguration": self.init_default_attr,
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
        Update the object from server's raw response

        @param dict_src:
        @return:
        """

        init_options = {
            "PolicyName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "PolicyARN": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "ServiceNamespace": self.init_default_attr,
            "ResourceId": self.init_default_attr,
            "ScalableDimension": self.init_default_attr,
            "PolicyType": self.init_default_attr,
            "StepScalingPolicyConfiguration": self.init_default_attr,
            "Alarms": self.init_default_attr,
            "CreationTime": self.init_default_attr,
            "TargetTrackingScalingPolicyConfiguration": self.init_default_attr,
        }
        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        request = dict()
        request["ServiceNamespace"] = self.service_namespace
        request["PolicyName"] = self.name
        request["ResourceId"] = self.resource_id
        request["ScalableDimension"] = self.scalable_dimension

        if self.policy_type is not None:
            request["PolicyType"] = self.policy_type

        if self.step_scaling_policy_configuration is not None:
            request["StepScalingPolicyConfiguration"] = self.step_scaling_policy_configuration

        if self.target_tracking_scaling_policy_configuration is not None:
            request["TargetTrackingScalingPolicyConfiguration"] = self.target_tracking_scaling_policy_configuration

        return request

    def generate_dispose_request(self):
        """
        Generate self disposing request.

        @return:
        """

        request = dict()
        request["ServiceNamespace"] = self.service_namespace
        request["PolicyName"] = self.name
        request["ResourceId"] = self.resource_id
        request["ScalableDimension"] = self.scalable_dimension
        return request

    @property
    def region(self):
        """
        This deployment's region

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
