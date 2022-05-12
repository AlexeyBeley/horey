"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class KMSKey(AwsObject):
    """
    AWS KMSKey class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "KeyArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "KeyId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
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
        self.dict_src = dict_src

        init_options = {
            "KeyId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "AWSAccountId": self.init_default_attr,
            "Arn": self.init_default_attr,
            "CreationDate": self.init_default_attr,
            "Enabled": self.init_default_attr,
            "Description": self.init_default_attr,
            "KeyUsage": self.init_default_attr,
            "KeyState": self.init_default_attr,
            "Origin": self.init_default_attr,
            "KeyManager": self.init_default_attr,
            "CustomerMasterKeySpec": self.init_default_attr,
            "EncryptionAlgorithms": self.init_default_attr,
            "MultiRegion": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def update_from_list_tags_response(self, dict_src):
        init_options = {
            "Tags": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def update_from_list_aliases_response(self, dict_src):
        init_options = {
            "Aliases": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        request = dict()
        request["KeyUsage"] = self.key_usage
        request["Description"] = self.description
        request["Tags"] = self.tags

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
