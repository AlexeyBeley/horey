"""
AWS SESIdentity representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class SESIdentity(AwsObject):
    """
    AWS SESIdentity class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        self.update_from_raw_response(dict_src)

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
        dict received from server.

        for key_name in dict_src: print(f"self.{self.format_attr_name(key_name)} = None")

        :param dict_src:
        :return:
        """

        init_options = {
            "DedicatedIpAutoWarmupEnabled": self.init_default_attr,
        }
        breakpoint()

        self.init_attrs(dict_src, init_options)
