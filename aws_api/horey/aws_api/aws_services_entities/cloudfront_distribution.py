"""
AWS Lambda representation
"""
import datetime
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
        self.comment = None

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
            "CallerReference": self.init_default_attr,
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

    def generate_create_request_with_tags(self):
        request = dict()
        request["DistributionConfigWithTags"] = {
            "DistributionConfig": self.distribution_config,
            "Tags": self.tags,
        }

        request["DistributionConfigWithTags"]["DistributionConfig"][
            "CallerReference"
        ] = str(datetime.datetime.now())
        return request

    def get_tag(self, key, ignore_missing_tag=False):
        if self.tags is None:
            if ignore_missing_tag:
                return None
            raise RuntimeError("No tags associated")
        for tag in self.tags["Items"]:
            tag_key_value = tag.get("Key")
            tag_key_value = (
                tag_key_value if tag_key_value is not None else tag.get("key")
            )

            if tag_key_value.lower() == key:
                tag_value_value = tag.get("Value")
                return (
                    tag_value_value if tag_value_value is not None else tag.get("value")
                )

        if ignore_missing_tag:
            return None

        raise RuntimeError(f"No tag '{key}' associated")

    def update_from_raw_create(self, dict_src):
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
            "InProgressInvalidationBatches": self.init_default_attr,
            "ActiveTrustedSigners": self.init_default_attr,
            "ActiveTrustedKeyGroups": self.init_default_attr,
            "DistributionConfig": self.init_default_attr,
            "CallerReference": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_invalidation(self, paths):
        dict_ret = {
            "DistributionId": self.id,
            "InvalidationBatch": {
                "Paths": {"Quantity": len(paths), "Items": paths},
                "CallerReference": str(datetime.datetime.now()),
            },
        }
        return dict_ret
