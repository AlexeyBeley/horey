"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from enum import Enum


class AMI(AwsObject):
    """
    AWS AvailabilityZone class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "ImageId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "Architecture": self.init_default_attr,
            "CreationDate": lambda x, y: self.init_date_attr_from_formatted_string(
                x, y, custom_format="%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            "ImageLocation": self.init_default_attr,
            "ImageType": self.init_default_attr,
            "Public": self.init_default_attr,
            "OwnerId": self.init_default_attr,
            "PlatformDetails": self.init_default_attr,
            "UsageOperation": self.init_default_attr,
            "State": self.init_default_attr,
            "BlockDeviceMappings": self.init_default_attr,
            "Hypervisor": self.init_default_attr,
            "RootDeviceType": self.init_default_attr,
            "VirtualizationType": self.init_default_attr,
            "Description": self.init_default_attr,
            "ImageOwnerAlias": self.init_default_attr,
            "Name": self.init_default_attr,
            "EnaSupport": self.init_default_attr,
            "RootDeviceName": self.init_default_attr,
            "SriovNetSupport": self.init_default_attr,
            "ProductCodes": self.init_default_attr,
            "Platform": self.init_default_attr,
            "BootMode": self.init_default_attr,
            "KernelId": self.init_default_attr,
            "RamdiskId": self.init_default_attr,
            "Tags": self.init_default_attr,
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

    def update_from_raw_response(self, dict_src):
        init_options = {
            "ImageId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "Architecture": self.init_default_attr,
            "CreationDate": lambda x, y: self.init_date_attr_from_formatted_string(
                x, y, custom_format="%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            "ImageLocation": self.init_default_attr,
            "ImageType": self.init_default_attr,
            "Public": self.init_default_attr,
            "OwnerId": self.init_default_attr,
            "PlatformDetails": self.init_default_attr,
            "UsageOperation": self.init_default_attr,
            "State": self.init_default_attr,
            "BlockDeviceMappings": self.init_default_attr,
            "Hypervisor": self.init_default_attr,
            "RootDeviceType": self.init_default_attr,
            "VirtualizationType": self.init_default_attr,
            "Description": self.init_default_attr,
            "ImageOwnerAlias": self.init_default_attr,
            "Name": self.init_default_attr,
            "EnaSupport": self.init_default_attr,
            "RootDeviceName": self.init_default_attr,
            "SriovNetSupport": self.init_default_attr,
            "ProductCodes": self.init_default_attr,
            "Platform": self.init_default_attr,
            "BootMode": self.init_default_attr,
            "KernelId": self.init_default_attr,
            "RamdiskId": self.init_default_attr,
            "Tags": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def get_status(self):
        return self.get_state()

    def get_state(self):
        if self.state == "pending":
            return self.State.PENDING
        elif self.state == "available":
            return self.State.AVAILABLE
        elif self.state == "invalid":
            return self.State.INVALID
        elif self.state == "deregistered":
            return self.State.DEREGISTERED
        elif self.state == "transient":
            return self.State.TRANSIENT
        elif self.state == "failed":
            return self.State.FAILED
        elif self.state == "error":
            return self.State.ERROR
        else:
            raise NotImplementedError(self.state)

    class State(Enum):
        PENDING = 0
        AVAILABLE = 1
        INVALID = 2
        DEREGISTERED = 3
        TRANSIENT = 4
        FAILED = 5
        ERROR = 6
