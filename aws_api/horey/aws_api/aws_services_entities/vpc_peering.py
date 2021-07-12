"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from enum import Enum


class VPCPeering(AwsObject):
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
            "VpcPeeringConnectionId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "AccepterVpcInfo": self.init_default_attr,
            "RequesterVpcInfo": self.init_default_attr,
            "Status": self.init_default_attr,
            "Tags": self.init_default_attr,
            "ExpirationTime": self.init_default_attr,
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
        request["PeerVpcId"] = self.peer_vpc_id
        request["VpcId"] = self.vpc_id
        request["PeerRegion"] = self.peer_region
        request["TagSpecifications"] = [{
            "ResourceType": "vpc-peering-connection",
            "Tags": self.tags}]

        return request

    def generate_accept_request(self):
        """
        PeerVpcId='string',
        VpcId='string',
        PeerRegion='string',
        """
        request = dict()
        request["VpcPeeringConnectionId"] = self.id

        return request

    def update_from_raw_response(self, dict_src):
        init_options = {
            "VpcPeeringConnectionId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "AccepterVpcInfo": self.init_default_attr,
            "RequesterVpcInfo": self.init_default_attr,
            "Status": self.init_default_attr,
            "Tags": self.init_default_attr,
            "ExpirationTime": self.init_default_attr,
                        }

        self.init_attrs(dict_src, init_options)

    def get_status(self):
        """
        """
        if self.status["Code"] == "initiating-request":
            return self.Status.INITIATING_REQUEST
        elif self.status["Code"] == "pending-acceptance":
            return self.Status.PENDING_ACCEPTANCE
        elif self.status["Code"] == "active":
            return self.Status.ACTIVE
        elif self.status["Code"] == "deleted":
            return self.Status.DELETED
        elif self.status["Code"] == "rejected":
            return self.Status.REJECTED
        elif self.status["Code"] == "failed":
            return self.Status.FAILED
        elif self.status["Code"] == "expired":
            return self.Status.EXPIRED
        elif self.status["Code"] == "provisioning":
            return self.Status.PROVISIONING
        elif self.status["Code"] == "deleting":
            return self.Status.DELETING
        else:
            raise NotImplementedError(self.status["Code"])

    class Status(Enum):
        INITIATING_REQUEST = 0
        PENDING_ACCEPTANCE = 1
        ACTIVE = 2
        DELETED = 3
        REJECTED = 4
        FAILED = 5
        EXPIRED = 6
        PROVISIONING = 7
        DELETING = 8

