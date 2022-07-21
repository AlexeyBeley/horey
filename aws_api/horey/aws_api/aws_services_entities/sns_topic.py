"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class SNSTopic(AwsObject):
    """
    AWS SNSTopic class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.attributes = None
        self.arn = None
        self._name = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "TopicArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
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
            "TopicArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        request = dict()
        request["Name"] = self.name
        request["Attributes"] = self.attributes
        request["Tags"] = self.tags

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
    
    @property
    def name(self):
        if self._name is None:
            try:
                self._name = self.arn.split(":")[5]
            except AttributeError as error_instance:
                raise RuntimeError("Both name and arn are None") from error_instance

        return self._name

    @name.setter
    def name(self, value):
        self._name = value
