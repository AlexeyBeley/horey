"""
Class to represent ec2 instance
"""
import pdb
from enum import Enum

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class EC2Volume(AwsObject):
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
            self._init_instance_from_cache(dict_src)
            return

        init_options = {
            "VolumeId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "Attachments": self.init_default_attr,
            "AvailabilityZone": self.init_default_attr,
            "CreateTime": self.init_default_attr,
            "Encrypted": self.init_default_attr,
            "KmsKeyId": self.init_default_attr,
            "Size": self.init_default_attr,
            "SnapshotId": self.init_default_attr,
            "State": self.init_default_attr,
            "Iops": self.init_default_attr,
            "Tags": self.init_default_attr,
            "VolumeType": self.init_default_attr,
            "MultiAttachEnabled": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

        tag_name = self.get_tagname("Name")
        self.name = tag_name if tag_name else self.id

    def _init_instance_from_cache(self, dict_src):
        """
        Init self from preserved dict.
        :param dict_src:
        :return:
        """
        options = {}

        self._init_from_cache(dict_src, options)

    def update_from_raw_response(self, dict_src):
        init_options = {
            "InstanceId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "NetworkInterfaces": self.init_interfaces,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        pdb.set_trace()
        request = dict()
        request["InstanceInitiatedShutdownBehavior"] = self.instance_initiated_shutdown_behavior
        return request

    def get_state(self):
        pdb.set_trace()
        if self.state["Name"] == "creating":
            return self.State.creating
        elif self.state["Name"] == "available":
            return self.State.available
        elif self.state["Name"] == "in-use":
            return self.State.in_use
        elif self.state["Name"] == "deleting":
            return self.State.deleting
        elif self.state["Name"] == "deleted":
            return self.State.deleted
        elif self.state["Name"] == "error":
            return self.State.error
        else:
            raise NotImplementedError(self.state["Name"])

    class State(Enum):
        creating = 0
        available = 1
        in_use = 2
        deleting = 3
        deleted = 4
        error = 5
