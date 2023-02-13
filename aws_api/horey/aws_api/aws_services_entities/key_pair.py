"""
EC2 key pair
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class KeyPair(AwsObject):
    """
    Main class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.key_type = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "KeyPairId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "KeyName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "KeyFingerprint": self.init_default_attr,
            "Tags": self.init_default_attr,
            "KeyType": self.init_default_attr,
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

    def generate_create_request(self):
        """
        Standard.

        :return:
        """

        request = {"KeyName": self.name, "TagSpecifications": [{"ResourceType": "key-pair", "Tags": self.tags}]}
        if self.key_type is not None:
            request["KeyType"] = self.key_type

        return request
