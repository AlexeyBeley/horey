"""
AWS Lambda representation
"""
import datetime
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class CloudfrontOriginAccessIdentity(AwsObject):
    """
    AWS identity representation class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "Id": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "S3CanonicalUserId": self.init_default_attr,
            "Comment": self.init_default_attr,
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
        request = dict()
        request["Comment"] = self.comment
        request["CallerReference"] = str(datetime.datetime.now())
        return {"CloudFrontOriginAccessIdentityConfig": request}
