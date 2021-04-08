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
            "Id": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "ARN": self.init_default_attr,
            "Status": self.init_default_attr,
            "LastModifiedTime": self.init_default_attr,
            "DomainName": self.init_default_attr,
            "Aliases": self.init_default_attr,
            "Origins": self.init_default_attr,
            "OriginGroups": self.init_default_attr,
            "DefaultCacheBehavior": self.init_default_attr,
            "CacheBehaviors": self.init_default_attr,
            "CustomErrorResponses": self.init_default_attr,
            "Comment": self.init_default_attr,
            "PriceClass": self.init_default_attr,
            "Enabled": self.init_default_attr,
            "ViewerCertificate": self.init_default_attr,
            "Restrictions": self.init_default_attr,
            "WebACLId": self.init_default_attr,
            "HttpVersion": self.init_default_attr,
            "IsIPV6Enabled": self.init_default_attr,
            "AliasICPRecordals": self.init_default_attr,
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

    def get_dns_records(self):
        """
        Get all self dns records.
        :return:
        """
        return [self.domain_name]
