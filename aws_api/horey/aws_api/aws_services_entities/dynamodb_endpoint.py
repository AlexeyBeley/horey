"""
AWS DynamoDBEndpoint representation
"""
from horey.aws_api.aws_services_entities.aws_object import AwsObject


class DynamoDBEndpoint(AwsObject):
    """
    AWS DynamoDBEndpoint class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "Address": self.init_default_attr,
            "CachePeriodInMinutes": self.init_default_attr,
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
