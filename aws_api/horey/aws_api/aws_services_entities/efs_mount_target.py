"""
AWS Lambda representation
"""
from enum import Enum

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class EFSMountTarget(AwsObject):
    """
    AWS VPC class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.life_cycle_state = None
        self.file_system_id = None
        self.subnet_id = None
        self.ip_address = None
        self.network_interface_id = None
        self.availability_zone_id = None
        self.availability_zone_name = None
        self.vpc_id = None
        self.owner_id = None
        self.security_groups = None

        self.request_key_to_attribute_mapping = {"MountTargetId": "id"}

        if from_cache:
            self._init_from_cache(dict_src, {})
            return

        self.update_from_raw_response(dict_src)

    def update_from_raw_response(self, dict_src):
        """
        Standard.

        :param dict_src:
        :return:
        """

        init_options = {
            "OwnerId": self.init_default_attr,
            "MountTargetId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "FileSystemId": self.init_default_attr,
            "SubnetId": self.init_default_attr,
            "NetworkInterfaceId": self.init_default_attr,
            "IpAddress": self.init_default_attr,
            "LifeCycleState": self.init_default_attr,
            "AvailabilityZoneId": self.init_default_attr,
            "AvailabilityZoneName": self.init_default_attr,
            "VpcId": self.init_default_attr,
            "SecurityGroups": self.init_default_attr,
        }
        return self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard.

        :return:
        """

        return self.generate_request(["FileSystemId", "SubnetId"],
                                     optional=["IpAddress", "SecurityGroups"],
                                     request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)

    def generate_dispose_request(self):
        """
        Standard.

        :return:
        """
        return self.generate_request(["MountTargetId"],
                                     request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)

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

    def generate_modify_mount_target_security_groups_request(self, desired_state):
        """
        Standard.

        :return:
        """

        required = ["MountTargetId"]
        optional = ["SecurityGroups"]
        self_request = self.generate_request(required,
                                             optional=optional,
                                             request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)
        desired_state_request = desired_state.generate_request(required,
                                                               optional=optional,
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
