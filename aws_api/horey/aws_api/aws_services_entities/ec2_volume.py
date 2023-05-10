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
        self.throughput = None
        self.multi_attach_enabled = None

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

    def generate_modify_request(self, desired_volume):
        """
        Standard.

        :return:
        """
        request = {}

        if desired_volume.iops and self.iops != desired_volume.iops:
            request["Iops"] = desired_volume.iops

        if desired_volume.size and self.size != desired_volume.size:
            request["Size"] = desired_volume.size

        if desired_volume.volume_type and self.volume_type != desired_volume.volume_type:
            request["VolumeType"] = desired_volume.volume_type

        if desired_volume.throughput and self.throughput != desired_volume.throughput:
            request["Throughput"] = desired_volume.throughput

        if desired_volume.multi_attach_enabled and self.multi_attach_enabled != desired_volume.multi_attach_enabled:
            request["MultiAttachEnabled"] = desired_volume.multi_attach_enabled

        if not request:
            return None

        request["VolumeId"] = self.id

        return request

    def get_status(self):
        """
        Return status.

        """
        return self.get_state()

    def get_state(self):
        """
        Get state.

        """
        mapping = {key.lower().replace("_", "-"): value for key, value in self.State.__members__.items()}
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
