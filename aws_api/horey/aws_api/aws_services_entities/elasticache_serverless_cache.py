"""
AWS object representation
"""
from enum import Enum

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.common_utils.common_utils import CommonUtils


# pylint: disable= too-many-instance-attributes
class ElasticacheServerlessCache(AwsObject):
    """
    Elasticache Cluster class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.subnet_ids = None
        self.engine = None
        self.description = None
        self.status = None
        self.cache_usage_limits = None
        self.remove_user_group = None
        self.user_group_id = None
        self.security_group_ids = None
        self.snapshot_retention_limit = None
        self.daily_snapshot_time = None
        self.major_engine_version = None

        self.request_key_to_attribute_mapping = {"ARN": "arn", "ServerlessCacheName": "name"}

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
            "ServerlessCacheName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "Description": self.init_default_attr,
            "CreateTime": self.init_default_attr,
            "Status": self.init_default_attr,
            "Engine": self.init_default_attr,
            "MajorEngineVersion": self.init_default_attr,
            "FullEngineVersion": self.init_default_attr,
            "SecurityGroupIds": self.init_default_attr,
            "Endpoint": self.init_default_attr,
            "ReaderEndpoint": self.init_default_attr,
            "SubnetIds": self.init_default_attr,
            "SnapshotRetentionLimit": self.init_default_attr,
            "DailySnapshotTime": self.init_default_attr,
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

    def generate_modify_request(self, desired_state):
        """
        Standard.

        :param desired_state:
        :return:
        """

        raise NotImplementedError("Do the same as in elasticache replication group")

    def generate_create_request(self):
        """
        Standard
        :return:
        """

        required = ["ServerlessCacheName", "Description", "SubnetIds", "Tags", "Engine"]
        optional = ["SecurityGroupIds"]
        self_request = self.generate_request(required,
                                             optional=optional,
                                             request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)

        return self_request

    def generate_dispose_request(self):
        """
        Standard
        :return:
        """

        required = ["ServerlessCacheName"]
        optional = []
        self_request = self.generate_request(required,
                                             optional=optional,
                                             request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)

        return self_request

    def generate_update_request(self, desired_cache):
        """
        Generate changes.

        :param desired_cache:
        :return:
        """

        required = ["ServerlessCacheName"]
        optional = ["Description", "CacheUsageLimits", "RemoveUserGroup", "UserGroupId", "SecurityGroupIds", "SnapshotRetentionLimit", "DailySnapshotTime",
                    "Engine", "MajorEngineVersion"]
        modify_request = self.generate_request_aws_object_modify(desired_cache, required,
                                           optional=optional,
                                           request_key_to_attribute_mapping=self.request_key_to_attribute_mapping,
                                           )

        return modify_request

    def get_status(self):
        """
        State string to enum.
        CREATING, AVAILABLE, DELETING, CREATE-FAILED and MODIFYING.

        :return:
        """

        if self.status is None:
            raise self.UndefinedStatusError()
        return self.Status.__members__[CommonUtils.camel_case_to_snake_case(self.status.replace("-", "_")).upper()]

    class Status(Enum):
        """
            for i, x in enumerate(ret): print(CommonUtils.camel_case_to_snake_case(x).upper() + " = " + str(i))

        """

        CREATING = 0
        AVAILABLE = 1
        DELETING = 2
        CREATE_FAILED =3
        MODIFYING = 4
