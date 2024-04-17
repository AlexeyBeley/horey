"""
Event bridge target representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class EventBridgeTarget(AwsObject):
    """
    AWS EventBridgeTarget class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None
        self.role_arn = None
        self.input = None
        self.ecs_parameters = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "Id": self.init_default_attr,
            "Arn": self.init_default_attr,
            "RoleArn": self.init_default_attr,
            "Input": self.init_default_attr,
            "EcsParameters": self.init_default_attr,
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
        """
        Standard

        @param dict_src:
        @return:
        """

        init_options = {
            "Id": self.init_default_attr,
            "Arn": self.init_default_attr,
            "RoleArn": self.init_default_attr,
            "Input": self.init_default_attr,
            "EcsParameters": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_put_request(self):
        """
        Standard

        @return:
        """
        request = {"Id": self.id, "Arn": self.arn}
        if self.role_arn is not None:
            request["RoleArn"] = self.role_arn

        if self.input is not None:
            request["Input"] = self.input

        if self.ecs_parameters is not None:
            request["EcsParameters"] = self.ecs_parameters

        return request

    @property
    def region(self):
        """
        Standard

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
        Standard

        @param value:
        @return:
        """
        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value
