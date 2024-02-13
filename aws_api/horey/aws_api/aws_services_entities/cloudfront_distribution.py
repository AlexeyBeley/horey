"""
Cloudfront distro

"""

import datetime

from enum import Enum
from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.common_utils.common_utils import CommonUtils
from horey.h_logger import get_logger

logger = get_logger()


class CloudfrontDistribution(AwsObject):
    """
    Main class

    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.comment = None
        self.distribution_config = {}
        self.tags = []
        self.domain_name = None
        self.arn = None
        self.aliases = None
        self.status = None
        self.e_tag = None

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

    def get_dns_records(self):
        """
        Get all self dns records.
        :return:
        """
        return [self.domain_name]

    def generate_create_request_with_tags(self):
        """
        Standard.

        :return:
        """

        request = {"DistributionConfigWithTags": {
            "DistributionConfig": self.distribution_config,
            "Tags": {"Items": self.tags},
        }}

        request["DistributionConfigWithTags"]["DistributionConfig"][
            "CallerReference"
        ] = str(datetime.datetime.now())
        return request

    def generate_update_request(self, desired_distribution):
        """
        Generate an update request with the desired distribution configuration, current id and current etag.

        WARNING: "Origins", "ViewerCertificate" are ignored!

        :return:
            The update request.

        """
        for self_distribution_config_key, self_distribution_config_value in self.distribution_config.items():
            desired_value = desired_distribution.distribution_config.get(self_distribution_config_key)
            if self_distribution_config_key in ["Origins", "ViewerCertificate"]:
                logger.warning(f"Ignoring cloud front distribution key: {self_distribution_config_key}")
                continue
            if desired_value is None:
                continue
            if self_distribution_config_value != desired_value:
                logger.info(
                    f"Found difference in cloud front distribution configuration in key: {self_distribution_config_key}")
                break
        else:
            return None

        if self.e_tag is None:
            raise RuntimeError(f"Cloudfront Distribution {self.id} ETag was not initialized")
        request = {
            "DistributionConfig": desired_distribution.distribution_config,
            "Id": self.id,
            "IfMatch": self.e_tag
        }
        request["DistributionConfig"]["CallerReference"] = self.distribution_config[
            "CallerReference"]
        for required_attr in ["Logging", "DefaultRootObject", "WebACLId", "CacheBehaviors", "Origins", "DefaultCacheBehavior", "Comment", "PriceClass", "Aliases", "HttpVersion",
                              "CustomErrorResponses", "ViewerCertificate", "Restrictions"]:
            if required_attr not in request["DistributionConfig"]:
                request["DistributionConfig"][required_attr] = self.distribution_config[required_attr]
        return request

    def update_from_raw_create(self, dict_src):
        """
        Standard.

        :param dict_src:
        :return:
        """
        self.update_from_raw_response(dict_src)

    def update_from_raw_response(self, dict_src):
        """
        Standard.

        :param dict_src:
        :return:
        """

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
            "Staging": self.init_default_attr,
            "ETag": self.init_default_attr
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_invalidation(self, paths):
        """
        Standard.

        :param paths:
        :return:
        """

        dict_ret = {
            "DistributionId": self.id,
            "InvalidationBatch": {
                "Paths": {"Quantity": len(paths), "Items": paths},
                "CallerReference": str(datetime.datetime.now()),
            },
        }
        return dict_ret

    def get_status(self):
        """
        For the status_waiter.

        :return:
        """

        if self.status is None:
            raise self.UndefinedStatusError()

        return self.Status.__members__[CommonUtils.camel_case_to_snake_case(self.status).upper()]

    class Status(Enum):
        """
            ret = ['PendingSpotBidPlacement' , 'WaitingForSpotInstanceRequestId' , 'WaitingForSpotInstanceId' ,
            'WaitingForInstanceId' , 'PreInService' , 'InProgress' , 'WaitingForELBConnectionDraining' ,
            'MidLifecycleAction' , 'WaitingForInstanceWarmup' , 'Successful' , 'Failed' ,
            'Cancelled' , 'WaitingForConnectionDraining']

            for i, x in enumerate(ret): print(CommonUtils.camel_case_to_snake_case(x).upper() + " = " + str(i))

        """

        DEPLOYED = 0
        IN_PROGRESS = 1
        FAILED = 2
