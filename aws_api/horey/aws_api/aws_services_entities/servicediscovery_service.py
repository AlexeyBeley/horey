"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class ServicediscoveryService(AwsObject):
    """
    ServicediscoveryService Service class
    """
    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.instances = []

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "Arn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "Id": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "Name": self.init_default_attr,
            "Type": self.init_default_attr,
            "DnsConfig": self.init_default_attr,
            "HealthCheckCustomConfig": self.init_default_attr,
            "CreateDate": self.init_default_attr,
            "Description": self.init_default_attr,
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

    def update_value_from_raw_response(self, raw_value):
        pdb.set_trace()
