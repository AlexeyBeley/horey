"""
AWS Lambda representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class ElasticacheCacheSecurityGroup(AwsObject):
    """
    Elasticache Cluster class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.cache_security_group_description = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "ARN": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "CacheSubnetGroupName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "CacheSubnetGroupDescription": self.init_default_attr,
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
        Standard

        :return:
        """
        request = {"CacheSecurityGroupName": self.cache_security_group_description, "Tags": self.tags}

        return request
