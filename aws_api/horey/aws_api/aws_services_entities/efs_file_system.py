"""
AWS Lambda representation
"""
from enum import Enum

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class EFSFileSystem(AwsObject):
    """
    AWS VPC class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.availability_zone_id = None
        self.throughput_mode = None
        self.provisioned_throughput_in_mibps = None
        self.file_system_protection = None
        self.life_cycle_state = None
        self.encrypted = None

        if from_cache:
            self._init_from_cache(dict_src, {})
            return

        self.request_key_to_attribute_mapping = {"FileSystemId": "id"}
        self.update_from_raw_response(dict_src)

    def update_from_raw_response(self, dict_src):
        """
        Standard.

        :param dict_src:
        :return:
        """

        init_options = {"ThroughputMode": self.init_default_attr,
                        "FileSystemId": lambda x, y: self.init_default_attr(
                            x, y, formatted_name="id"
                        ),
                        "ProvisionedThroughputInMibps": lambda x, y: self.init_default_attr(x, float(y)),
                        "OwnerId": self.init_default_attr,
                        "CreationToken": self.init_default_attr,
                        "FileSystemArn": lambda x, y: self.init_default_attr(
                            x, y, formatted_name="arn"
                        ),
                        "CreationTime": self.init_default_attr,
                        "LifeCycleState": self.init_default_attr,
                        "Name": self.init_default_attr,
                        "NumberOfMountTargets": self.init_default_attr,
                        "SizeInBytes": self.init_default_attr,
                        "PerformanceMode": self.init_default_attr,
                        "Encrypted": self.init_default_attr,
                        "KmsKeyId": self.init_default_attr,
                        "AvailabilityZoneName": self.init_default_attr,
                        "AvailabilityZoneId": self.init_default_attr,
                        "Tags": self.init_default_attr,
                        "FileSystemProtection": self.init_default_attr,
                        }

        return self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard.

        :return:
        """

        if not self.get_tagname():
            raise RuntimeError("Tag Name was not set")

        return self.generate_request([],
                                     optional=["ThroughputMode", "ProvisionedThroughputInMibps", "Encrypted", "Tags"],
                                     request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)

    def generate_dispose_request(self):
        """
        Standard.

        :return:
        """
        return self.generate_request(["FileSystemId"],
                                     request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)

    def generate_update_request(self, desired_state):
        """
        Standard.

        :return:
        """

        required = ["FileSystemId"]
        self_request = self.generate_request(required,
                              optional=["ThroughputMode", "ProvisionedThroughputInMibps"],
                              request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)
        desired_state_request = desired_state.generate_request(required,
                              optional=["ThroughputMode", "ProvisionedThroughputInMibps"],
                              request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)

        request = {}
        for key in required:
            if self_request[key] != desired_state_request[key]:
                raise ValueError(f"Required key must be same: {key}")
            request[key] = desired_state_request[key]

        for key, desired_value in desired_state_request.items():
            if self_request.get(key) != desired_value:
                request[key] = desired_state_request[key]

        return None if len(request) == len(required) else request

    def get_tagname(self, ignore_missing_tag=False):
        """
        Name tag.

        :return:
        """

        if ignore_missing_tag:
            raise ValueError(f"Should not set {ignore_missing_tag=}")

        return self.get_tag("Name", casesensitive=True)

    def get_status(self):
        """
        Standard.

        :return:
        """
        if self.life_cycle_state is None:
            raise self.UndefinedStatusError("life_cycle_state was not set")
        for enum_value in self.State.__members__.values():
            if enum_value.value == self.life_cycle_state:
                return enum_value
        raise KeyError(f"Has no state configured for value: '{self.life_cycle_state=}'")

    class State(Enum):
        """
        Standard

        """

        CREATING = "creating"
        AVAILABLE = "available"
        UPDATING = "updating"
        DELETING = "deleting"
        DELETED = "deleted"
        ERROR = "error"
