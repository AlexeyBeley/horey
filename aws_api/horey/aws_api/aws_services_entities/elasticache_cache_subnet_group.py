"""
AWS Elasticache representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class ElasticacheCacheSubnetGroup(AwsObject):
    """
    Elasticache Cluster class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.cache_subnet_group_description = None
        self.subnet_ids = None

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
        Standard.

        :param dict_src:
        :return:
        """

        init_options = {
            "ARN": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "CacheSubnetGroupName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "CacheSubnetGroupDescription": self.init_default_attr,
            "VpcId": self.init_default_attr,
            "Subnets": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard.

        :return:
        """
        request = {"CacheSubnetGroupName": self.name,
                   "CacheSubnetGroupDescription": self.cache_subnet_group_description, "SubnetIds": self.subnet_ids,
                   "Tags": self.tags}

        return request
