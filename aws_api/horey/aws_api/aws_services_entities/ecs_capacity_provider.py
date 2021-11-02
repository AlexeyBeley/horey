"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class ECSCapacityProvider(AwsObject):
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
            "capacityProviderArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "status": self.init_default_attr,
            "name": self.init_default_attr,
            "tags": self.init_default_attr,
            "autoScalingGroupProvider": self.init_default_attr,
            "updateStatus": self.init_default_attr,
            "updateStatusReason": self.init_default_attr,
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
            "capacityProviderArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "status": self.init_default_attr,
            "name": self.init_default_attr,
            "tags": self.init_default_attr,
            "autoScalingGroupProvider": self.init_default_attr,
            "updateStatus": self.init_default_attr,
            "updateStatusReason": self.init_default_attr,
        }
        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        request = dict()
        request["name"] = self.name
        request["autoScalingGroupProvider"] = self.auto_scaling_group_provider
        request["tags"] = self.tags
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
