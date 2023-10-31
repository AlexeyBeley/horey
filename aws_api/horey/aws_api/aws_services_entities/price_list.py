"""
Class to represent price list
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class PriceList(AwsObject):
    """
    Class to represent ec2 instance
    """

    def __init__(self, dict_src, from_cache=False):
        """
        Init EC2 instance with boto3 dict
        :param dict_src:
        """
        super().__init__(dict_src)
        self.encrypted = None

        if from_cache:
            self._init_objects_from_cache(dict_src)
            return

        self.update_from_raw_response(dict_src)

    def _init_objects_from_cache(self, dict_src):
        """
        Init self from preserved dict.

        :param dict_src:
        :return:
        """

        options = {}

        self._init_from_cache(dict_src, options)

    def update_from_raw_response(self, dict_src):
        """
        dict_src from create volume request.

        :param dict_src:
        :return:
        """

        init_options = {
            "formatVersion": self.init_default_attr,
            "disclaimer": self.init_default_attr,
            "offerCode": self.init_default_attr,
            "version": self.init_default_attr,
            "publicationDate": self.init_default_attr,
            "products": self.init_default_attr,
            "terms": self.init_default_attr,
            "attributesList": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options, raise_on_no_option=True)
