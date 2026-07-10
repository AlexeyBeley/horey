"""
AWS ElasticacheReplicationGroup representation
"""
from enum import Enum

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.common_utils.common_utils import CommonUtils


# pylint: disable= too-many-instance-attributes
class ElasticacheUser(AwsObject):
    """
    Elasticache Cluster class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.status = None
        self.user_name = None
        self.engine = None
        self.access_string = None

        self.passwords = None
        self.no_password_required = None
        self.authentication_mode = None
        self.append_access_string = None

        self.request_key_to_attribute_mapping = {"ARN": "arn", "UserId": "id"}

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
            "UserId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "UserName": self.init_default_attr,
            "Engine": self.init_default_attr,
            "Status": self.init_default_attr,
            "MinimumEngineVersion": self.init_default_attr,
            "AccessString": self.init_default_attr,
            "UserGroupIds": self.init_default_attr,
            "Authentication": self.init_default_attr,
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

        ACTIVE = 0
        MODIFYING = 1
        DELETING = 2

    def generate_create_request(self):
        """
        Generate raw dict request.

        @return:
        """

        if not self.tags:
            raise RuntimeError("Tags required when creating access entry")

        request = {"UserId": self.id,
                   "UserName": self.user_name,
                   "Engine": self.engine,
                   "AccessString": self.access_string,
                   "Tags": self.tags}

        self.extend_request_with_optional_parameters(request, ["Passwords",
                                                               "NoPasswordRequired",
                                                               "AuthenticationMode",
                                                               ])

        return request

    def generate_modify_request(self, desired_state):
        """
        Standard.

        :param desired_state:
        :return:
        """

        return self.generate_request_aws_object_modify(desired_state, ["UserId"],
                                                       optional=["AccessString",
                                                                 "AppendAccessString",
                                                                 "Passwords",
                                                                 "NoPasswordRequired",
                                                                 "AuthenticationMode",
                                                                 "Engine"
                                                                 ],
                                                       request_key_to_attribute_mapping=self.request_key_to_attribute_mapping,
                                                       )



