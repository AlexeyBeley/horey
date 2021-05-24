"""
Class to represent ec2 spot fleet request
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.aws_services_entities.network_interface import NetworkInterface


class EC2SpotFleetRequest(AwsObject):
    """
    Class to represent ec2 instance
    """

    def __init__(self, dict_src, from_cache=False):
        """
        Init EC2 instance with boto3 dict
        :param dict_src:
        """
        super().__init__(dict_src)

        if from_cache:
            self._init_spot_fleet_request_from_cache(dict_src)
            return

        init_options = {
            "SpotFleetRequestId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "ActivityStatus": self.init_default_attr,
            "CreateTime": self.init_default_attr,
            "SpotFleetRequestConfig": self.init_default_attr,
            "SpotFleetRequestState": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def _init_spot_fleet_request_from_cache(self, dict_src):
        """
        Init self from preserved dict.
        :param dict_src:
        :return:
        """
        options = {}

        self._init_from_cache(dict_src, options)
