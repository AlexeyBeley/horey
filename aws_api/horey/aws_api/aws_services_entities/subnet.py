"""
AWS EC2 Subnet representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class Subnet(AwsObject):
    """
    Main class

    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.instances = []
        self._region = None
        self.cidr_block = None
        self.vpc_id = None
        self.availability_zone_id = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "SubnetId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "SubnetArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
            "AvailabilityZone": self.init_default_attr,
            "AvailabilityZoneId": self.init_default_attr,
            "AvailableIpAddressCount": self.init_default_attr,
            "CidrBlock": self.init_default_attr,
            "DefaultForAz": self.init_default_attr,
            "MapPublicIpOnLaunch": self.init_default_attr,
            "MapCustomerOwnedIpOnLaunch": self.init_default_attr,
            "State": self.init_default_attr,
            "VpcId": self.init_default_attr,
            "OwnerId": self.init_default_attr,
            "AssignIpv6AddressOnCreation": self.init_default_attr,
            "Ipv6CidrBlockAssociationSet": self.init_default_attr,
            "Tags": self.init_default_attr,
            "PrivateDnsNameOptionsOnLaunch": self.init_default_attr,
            "EnableDns64": self.init_default_attr,
            "Ipv6Native": self.init_default_attr,
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
        """
        Generate create request dictionary.

        @return:
        """

        for tag in self.tags:
            if tag["Key"] == "name":
                tag["Key"] = "Name"

        request = {"CidrBlock": self.cidr_block, "AvailabilityZoneId": self.availability_zone_id, "VpcId": self.vpc_id,
                   "TagSpecifications": [{"ResourceType": "subnet", "Tags": self.tags}]}

        return request

    def update_from_raw_create(self, dict_src):
        """
        Update self from raw server response to create api call.

        @param dict_src:
        @return:
        """

        init_options = {
            "SubnetId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "SubnetArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
            "AvailabilityZone": self.init_default_attr,
            "AvailabilityZoneId": self.init_default_attr,
            "AvailableIpAddressCount": self.init_default_attr,
            "CidrBlock": self.init_default_attr,
            "DefaultForAz": self.init_default_attr,
            "MapPublicIpOnLaunch": self.init_default_attr,
            "MapCustomerOwnedIpOnLaunch": self.init_default_attr,
            "State": self.init_default_attr,
            "VpcId": self.init_default_attr,
            "OwnerId": self.init_default_attr,
            "AssignIpv6AddressOnCreation": self.init_default_attr,
            "Ipv6CidrBlockAssociationSet": self.init_default_attr,
            "Tags": self.init_default_attr,
            "PrivateDnsNameOptionsOnLaunch": self.init_default_attr,
            "EnableDns64": self.init_default_attr,
            "Ipv6Native": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    @property
    def region(self):
        """
        Self region.

        @return:
        """

        if self._region is not None:
            return self._region

        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        """
        Region setter.

        @param value:
        @return:
        """

        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value
