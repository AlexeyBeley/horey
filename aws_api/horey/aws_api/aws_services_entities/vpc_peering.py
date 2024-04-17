"""
AWS object representation
"""
from enum import Enum
from horey.aws_api.aws_services_entities.aws_object import AwsObject


class VPCPeering(AwsObject):
    """
    AWS object class
    """

    def __init__(self, dict_src, from_cache=False):
        self._peer_vpc_id = None
        self._vpc_id = None
        self._peer_region = None
        self.requester_vpc_info = {}
        self.accepter_vpc_info = {}
        self.status = {}
        super().__init__(dict_src)
        self.instances = []

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "VpcPeeringConnectionId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "AccepterVpcInfo": self.init_default_attr,
            "RequesterVpcInfo": self.init_default_attr,
            "Status": self.init_default_attr,
            "Tags": self.init_default_attr,
            "ExpirationTime": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    @property
    def vpc_id(self):
        """
        Find vpc_id
        :return:
        """
        if self._vpc_id is None:
            self._vpc_id = self.requester_vpc_info["VpcId"]
        return self._vpc_id

    @vpc_id.setter
    def vpc_id(self, value):
        self._vpc_id = value

    @property
    def peer_vpc_id(self):
        """
        Find peer_vpc_id
        :return:
        """
        if self._peer_vpc_id is None:
            self._peer_vpc_id = self.accepter_vpc_info["VpcId"]
        return self._peer_vpc_id

    @peer_vpc_id.setter
    def peer_vpc_id(self, value):
        self._peer_vpc_id = value

    @property
    def peer_region(self):
        """
        Find peer_region
        :return:
        """
        if self._peer_region is None:
            self._peer_region = self.requester_vpc_info["Region"]
        return self._peer_region

    @peer_region.setter
    def peer_region(self, value):
        self._peer_region = value

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
        request = {"PeerVpcId": self.peer_vpc_id,
                   "VpcId": self.vpc_id,
                   "PeerRegion": self.peer_region,
                   "TagSpecifications": [
                       {"ResourceType": "vpc-peering-connection", "Tags": self.tags}
                   ]}

        return request

    def generate_accept_request(self):
        """
        PeerVpcId='string',
        VpcId='string',
        PeerRegion='string',
        """
        request = {"VpcPeeringConnectionId": self.id}

        return request

    def update_from_raw_response(self, dict_src):
        """
        Standard
        :param dict_src:
        :return:
        """
        init_options = {
            "VpcPeeringConnectionId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "AccepterVpcInfo": self.init_default_attr,
            "RequesterVpcInfo": self.init_default_attr,
            "Status": self.init_default_attr,
            "Tags": self.init_default_attr,
            "ExpirationTime": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    # pylint: disable= too-many-return-statements
    def get_status(self):
        """
        Standard
        :return:
        """
        if self.status["Code"] == "initiating-request":
            return self.Status.INITIATING_REQUEST
        if self.status["Code"] == "pending-acceptance":
            return self.Status.PENDING_ACCEPTANCE
        if self.status["Code"] == "active":
            return self.Status.ACTIVE
        if self.status["Code"] == "deleted":
            return self.Status.DELETED
        if self.status["Code"] == "rejected":
            return self.Status.REJECTED
        if self.status["Code"] == "failed":
            return self.Status.FAILED
        if self.status["Code"] == "expired":
            return self.Status.EXPIRED
        if self.status["Code"] == "provisioning":
            return self.Status.PROVISIONING
        if self.status["Code"] == "deleting":
            return self.Status.DELETING

        raise NotImplementedError(self.status["Code"])

    class Status(Enum):
        """
        Stanadrd
        """
        INITIATING_REQUEST = 0
        PENDING_ACCEPTANCE = 1
        ACTIVE = 2
        DELETED = 3
        REJECTED = 4
        FAILED = 5
        EXPIRED = 6
        PROVISIONING = 7
        DELETING = 8
