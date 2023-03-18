"""
Class to represent ec2 instance
"""
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
        self.encrypted = None
        self.availability_zone = None
        self.iops = None
        self.size = None
        self.volume_type = None
        self.state = None
        self.id = None

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
        """
        dict_src from create volume request.

        :param dict_src:
        :return:
        """

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

    def generate_create_request(self):
        """
        Standard.

        :return:
        """

        request = {"Encrypted": self.encrypted,
                   "AvailabilityZone": self.availability_zone,
                   "Iops": self.iops,
                   "Size": self.size,
                   "VolumeType": self.volume_type,
                   "TagSpecifications": [{"ResourceType": "volume", "Tags": self.tags}]}

        return request

    def get_state(self):
        """
        Get state.

        """
        mapping = {key.lower(): value for key, value in self.State.__members__.items()}
        return mapping[self.state]

    class State(Enum):
        """
        Volume state.

        """

        CREATING = 0
        AVAILABLE = 1
        IN_USE = 2
        DELETING = 3
        DELETED = 4
        ERROR = 5
