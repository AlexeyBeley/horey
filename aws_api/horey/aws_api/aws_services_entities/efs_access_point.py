"""
AWS Lambda representation
"""
from enum import Enum

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class EFSAccessPoint(AwsObject):
    """
    AWS VPC class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.life_cycle_state = None
        self.client_token = None
        self.file_system_id = None
        self.posix_user = None
        self.root_directory = None
        self.owner_id = None
        self.request_key_to_attribute_mapping = {"AccessPointId": "id"}

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
            "AccessPointId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "AccessPointArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"),
            "ClientToken": self.init_default_attr,
            "Name": self.init_default_attr,
            "Tags": self.init_default_attr,
            "FileSystemId": self.init_default_attr,
            "PosixUser": self.init_default_attr,
            "RootDirectory": self.init_default_attr,
            "OwnerId": self.init_default_attr,
            "LifeCycleState": self.init_default_attr,
        }
        return self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard.

        :return:
        """

        if not self.get_tagname():
            raise RuntimeError("Tag Name was not set")

        return self.generate_request(["FileSystemId", "Tags"],
                                     optional=["RootDirectory", "PosixUser", "ClientToken"],
                                     request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)

    def generate_dispose_request(self):
        """
        Standard.

        :return:
        """
        return self.generate_request(["AccessPointId"],
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
