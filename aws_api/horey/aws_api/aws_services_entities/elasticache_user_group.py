"""
AWS ElasticacheReplicationGroup representation
"""
from enum import Enum

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.common_utils.common_utils import CommonUtils


# pylint: disable= too-many-instance-attributes
class ElasticacheUserGroup(AwsObject):
    """
    Elasticache Cluster class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.status = None
        self.engine = None
        self.user_ids = None
        self.user_ids_to_add = None
        self.user_ids_to_remove = None

        self.request_key_to_attribute_mapping = {"ARN": "arn", "UserGroupId": "id"}

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        self.update_from_raw_response(dict_src)

    def update_from_raw_response(self, dict_src):
        """
        From AWS response.
        :param dict_src:
        :return:
        """
        init_options = {
            "ARN": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "UserGroupId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "Status": self.init_default_attr,
            "Engine": self.init_default_attr,
            "UserIds": self.init_default_attr,
            "MinimumEngineVersion": self.init_default_attr,
            "PendingChanges": self.init_default_attr,
            "ReplicationGroups": self.init_default_attr,
            "ServerlessCaches": self.init_default_attr,
        }

        return self.init_attrs(dict_src, init_options)

    def _init_object_from_cache(self, dict_src):
        """
        Init from cache
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def get_status(self):
        """
        For the status_waiter.

        :return:
        """

        if self.status is None:
            raise self.UndefinedStatusError("Status")

        return self.Status.__members__[CommonUtils.camel_case_to_snake_case(self.status).upper()]

    class Status(Enum):
        """
        Standard
        """

        CREATING = 0
        ACTIVE = 1
        MODIFYING = 2
        DELETING = 3


    def generate_create_request(self):
        """
        Generate raw dict request.

        @return:
        """

        if not self.tags:
            raise RuntimeError("Tags required when creating access entry")

        request = {"UserGroupId": self.id,
                   "Engine": self.engine,
                   "Tags": self.tags,
                   "UserIds": self.user_ids}

        return request

    def generate_modify_request(self, desired_state):
        """
        Standard.

        :param desired_state:
        :return:
        """

        return self.generate_request_aws_object_modify(desired_state, ["UserGroupId"],
                                                       optional=["UserIdsToAdd",
                                                                 "UserIdsToRemove",
                                                                 "Engine"
                                                                 ],
                                                       request_key_to_attribute_mapping=self.request_key_to_attribute_mapping,
                                                           )
