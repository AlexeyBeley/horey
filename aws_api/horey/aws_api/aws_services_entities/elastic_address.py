"""
AWS Lambda representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class ElasticAddress(AwsObject):
    """
    AWS AvailabilityZone class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.instance_id = None
        self.public_ip = None
        self.association_id = None
        self.domain = None
        self.network_interface_id = None
        self.network_interface_owner_id = None
        self.private_ip_address = None
        self.tags = None
        self.public_ipv4_pool = None
        self.network_border_group = None

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
            "AllocationId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "InstanceId": self.init_default_attr,
            "PublicIp": self.init_default_attr,
            "AssociationId": self.init_default_attr,
            "Domain": self.init_default_attr,
            "NetworkInterfaceId": self.init_default_attr,
            "NetworkInterfaceOwnerId": self.init_default_attr,
            "PrivateIpAddress": self.init_default_attr,
            "Tags": self.init_default_attr,
            "PublicIpv4Pool": self.init_default_attr,
            "NetworkBorderGroup": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard.

        :return:
        """
        request = {}
        request["TagSpecifications"] = [
            {"ResourceType": "elastic-ip", "Tags": self.tags}
        ]

        return request

    @property
    def name(self):
        return self.get_tagname(ignore_missing_tag=True)

    @name.setter
    def name(self, value):
        if value is not None:
            raise ValueError(value)
