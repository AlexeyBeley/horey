"""
AWS Lambda representation
"""
import sys
import os
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class CloudfrontDistribution(AwsObject):
    """
    Lambda representation class
    """
    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "Something": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "ARN": self.init_default_attr,
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

    def get_assinged_security_group_ids(self):
        lst_ret = []
        if self.vpc_config is not None:
            return self.vpc_config["SecurityGroupIds"]
        return lst_ret