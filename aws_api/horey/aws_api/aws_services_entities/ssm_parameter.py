"""
SSMParameter representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class SSMParameter(AwsObject):
    """
    AWS SSMParameter class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "Name": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "Type": self.init_default_attr,
            "Value": self.init_default_attr,
            "Version": self.init_default_attr,
            "Selector": self.init_default_attr,
            "SourceResult": self.init_default_attr,
            "LastModifiedDate": self.init_default_attr,
            "ARN": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "DataType": self.init_default_attr,
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

    @property
    def region(self):
        if self._region is not None:
            return self._region

        raise NotImplementedError()

    @region.setter
    def region(self, value):
        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value
