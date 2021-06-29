"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class NatGateway(AwsObject):
    """
    AWS AvailabilityZone class
    """
    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.instances = []

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "NatGatewayId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "CreateTime": self.init_default_attr,
            "NatGatewayAddresses": self.init_default_attr,
            "State": self.init_default_attr,
            "SubnetId": self.init_default_attr,
            "VpcId": self.init_default_attr,
            "Tags": self.init_default_attr,
            "ConnectivityType": self.init_default_attr,
            "DeleteTime": self.init_default_attr,
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
        PeerVpcId='string',
        VpcId='string',
        PeerRegion='string',
        """
        request = dict()
        request["SubnetId"] = self.subnet_id
        request["AllocationId"] = self.allocation_id
        request["TagSpecifications"] = [{
            "ResourceType": "natgateway",
            "Tags": self.tags}]

        return request

    def update_from_raw_response(self, dict_src):
        init_options = {
            "NatGatewayId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "CreateTime": self.init_default_attr,
            "NatGatewayAddresses": self.init_default_attr,
            "State": self.init_default_attr,
            "SubnetId": self.init_default_attr,
            "VpcId": self.init_default_attr,
            "Tags": self.init_default_attr,
            "ConnectivityType": self.init_default_attr,
            "DeleteTime": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

