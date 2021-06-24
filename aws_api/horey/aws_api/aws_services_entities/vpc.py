"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class VPC(AwsObject):
    """
    AWS VPC class
    """
    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.instances = []
        self.cidr_block = None
        self.region = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
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
        AmazonProvidedIpv6CidrBlock=True|False,
        Ipv6Pool='string',
        Ipv6CidrBlock='string',
        DryRun=True|False,
        InstanceTenancy='default'|'dedicated'|'host',
        Ipv6CidrBlockNetworkBorderGroup='string',
        TagSpecifications=
        )
       """
        request = dict()
        request["CidrBlock"] = self.cidr_block
        request["TagSpecifications"] = [{
                                        "ResourceType": "vpc",
                                        "Tags": self.tags}]

        return request

    def update_from_raw_create(self, dict_src):
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
                        }

        self.init_attrs(dict_src, init_options)

