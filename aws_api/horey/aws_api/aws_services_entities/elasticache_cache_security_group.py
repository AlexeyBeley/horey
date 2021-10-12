"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class ElasticacheCacheSecurityGroup(AwsObject):
    """
    Elasticache Cluster class
    """
    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.instances = []

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "ARN": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "CacheSubnetGroupName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "CacheSubnetGroupDescription":  self.init_default_attr,
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

    def update_from_raw_response(self, raw_value):
        pdb.set_trace()

    def generate_create_request(self):
        request = dict()
        request["CacheSecurityGroupName"] = self.name
        request["CacheSecurityGroupName"] = self.cache_security_group_description
        request["Tags"] = self.tags

        return request

    def generate_authorize_request(self, existing_security_group=None):
        """
        response = client.authorize_cache_security_group_ingress(
        CacheSecurityGroupName='string',
        EC2SecurityGroupName='string',
        EC2SecurityGroupOwnerId='string'
        )
        @return:
        """
        pdb.set_trace()
        if existing_security_group is not None:
            pdb.set_trace()
        request = dict()
        request["CacheSecurityGroupName"] = self.name
        request["EC2SecurityGroupName"] = self.cache_security_group_description
        request["EC2SecurityGroupOwnerId"] = self.tags

        return request
