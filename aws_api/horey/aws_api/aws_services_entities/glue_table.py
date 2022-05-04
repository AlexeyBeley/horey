"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class GlueTable(AwsObject):
    """
    AWS GlueTable class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "Name": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "DatabaseName": self.init_default_attr,
            "Owner": self.init_default_attr,
            "CreateTime": self.init_default_attr,
            "UpdateTime": self.init_default_attr,
            "LastAccessTime": self.init_default_attr,
            "Retention": self.init_default_attr,
            "StorageDescriptor": self.init_default_attr,
            "PartitionKeys": self.init_default_attr,
            "TableType": self.init_default_attr,
            "Parameters": self.init_default_attr,
            "CreatedBy": self.init_default_attr,
            "IsRegisteredWithLakeFormation": self.init_default_attr,
            "CatalogId": self.init_default_attr,
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

    def update_from_raw_response(self, raw_value):
        raise NotImplementedError()

    def generate_create_request(self):
        pdb.set_trace()
        request = dict()
        request["Name"] = self.name
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
