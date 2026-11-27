"""
AWS EC2 NAT representation
"""
from enum import Enum
from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.network.ip import IP


class NatGateway(AwsObject):
    """
    AWS AvailabilityZone class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.nat_gateway_addresses = []
        self.subnet_id = None
        self.allocation_id = None
        self.state = None

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
        PeerVpcId='string',
        VpcId='string',
        PeerRegion='string',
        """
        request = {"SubnetId": self.subnet_id,
                   "AllocationId": self.allocation_id,
                   "TagSpecifications": [
                       {"ResourceType": "natgateway", "Tags": self.tags}
                   ]}

        return request

    def generate_dispose_request(self, dry_run=False):
        """
        Standard.

        :return:
        """
        request = {"NatGatewayId": self.id, "DryRun": dry_run}
        return request

    def update_from_raw_response(self, dict_src):
        """
        Update from AWS API dict.

        :param dict_src:
        :return:
        """

        init_options = {
            "NatGatewayId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "CreateTime": self.init_default_attr,
            "NatGatewayAddresses": self.init_default_attr,
            "State": self.init_default_attr,
            "SubnetId": self.init_default_attr,
            "VpcId": self.init_default_attr,
            "Tags": self.init_default_attr,
            "ConnectivityType": self.init_default_attr,
            "DeleteTime": self.init_default_attr,
            "FailureCode": self.init_default_attr,
            "FailureMessage": self.init_default_attr,
            "AttachedAppliances": self.init_default_attr,
            "AvailabilityMode": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def get_public_ip_addresses(self):
        """
        Get all the public IPs

        @return:
        """

        return [
            IP(address["PublicIp"], int_mask=32)
            for address in self.nat_gateway_addresses
        ]

    @property
    def name(self):
        """
        Tag based.

        :return:
        """
        return self.get_tagname(ignore_missing_tag=True)

    @name.setter
    def name(self, value):
        """
        Set the value.

        :param value:
        :return:
        """

        if value is None:
            return
        raise NotImplementedError(value)

    def get_state(self):
        """
        Get enum state.

        :return:
        """

        if self.state == "available":
            return self.State.AVAILABLE
        if self.state == "deleted":
            return self.State.DELETED
        if self.state == "pending":
            return self.State.PENDING
        if self.state == "failed":
            return self.State.FAILED
        if self.state == "deleting":
            return self.State.DELETING
        raise ValueError(self.state)

    class State(Enum):
        """
        Available states
        """
        PENDING = 0
        AVAILABLE = 1
        DELETED = 2
        DELETING = 3
        FAILED = 4
