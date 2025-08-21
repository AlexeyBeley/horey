"""
AWS VPC representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.network.ip import IP


class VPC(AwsObject):
    """
    AWS VPC class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.instances = []
        self.cidr_block = None
        self.enable_dns_hostnames = True
        self.enable_dns_support = True
        self.cidr_block_association_set = []

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

    def generate_create_request(self):
        """
        AmazonProvidedIpv6CidrBlock=True|False,
        Ipv6Pool='string',
        Ipv6CidrBlock='string',
        DryRun=True|False,
        InstanceTenancy='default'|'dedicated'|'host',
        Ipv6CidrBlockNetworkBorderGroup='string',
        TagSpecifications=
        )
        """

        request = {}
        request["CidrBlock"] = self.cidr_block
        request["TagSpecifications"] = [{"ResourceType": "vpc", "Tags": self.tags}]

        return request

    def generate_modify_vpc_attribute_requests(self, desired=None):
        """
        Standard.

        :param desired:
        :return:
        """
        lst_ret = []
        if not desired or self.enable_dns_hostnames != desired.enable_dns_hostnames:
            request = {"EnableDnsHostnames": {"Value": self.enable_dns_hostnames}, "VpcId": self.id}
            lst_ret.append(request)

        if not desired or self.enable_dns_support != desired.enable_dns_support:
            request = {"EnableDnsSupport": {"Value": self.enable_dns_support}, "VpcId": self.id}
            lst_ret.append(request)

        return lst_ret

    def update_from_raw_create(self, dict_src):
        """
        Backward compatible.

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
            "VpcId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "CidrBlock": self.init_default_attr,
            "DhcpOptionsId": self.init_default_attr,
            "State": self.init_default_attr,
            "OwnerId": self.init_default_attr,
            "InstanceTenancy": self.init_default_attr,
            "CidrBlockAssociationSet": self.init_default_attr,
            "IsDefault": self.init_default_attr,
            "Tags": self.init_default_attr,
            "Ipv6CidrBlockAssociationSet": self.init_default_attr,
            "BlockPublicAccessStates": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    @property
    def name(self):
        """
        Tag name.

        :return:
        """
        return self.get_tagname(ignore_missing_tag=True)

    @name.setter
    def name(self, value):
        """
        For default initiation.

        :param value:
        :return:
        """
        if value is None:
            return
        raise NotImplementedError()

    def get_associated_cidr_ips(self):
        """
        Except the main cidr.

        :return:
        """

        return [
            IP(association_set["CidrBlock"])
            for association_set in self.cidr_block_association_set
        ]
