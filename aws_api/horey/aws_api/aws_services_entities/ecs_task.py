"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region
from enum import Enum


class ECSTask(AwsObject):
    """
    AWS ECSService class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "taskArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "attachments": self.init_default_attr,
            "attributes": self.init_default_attr,
            "availabilityZone": self.init_default_attr,
            "clusterArn": self.init_default_attr,
            "connectivity": self.init_default_attr,
            "connectivityAt": self.init_default_attr,
            "containerInstanceArn": self.init_default_attr,
            "containers": self.init_default_attr,
            "cpu": self.init_default_attr,
            "createdAt": self.init_default_attr,
            "desiredStatus": self.init_default_attr,
            "enableExecuteCommand": self.init_default_attr,
            "group": self.init_default_attr,
            "healthStatus": self.init_default_attr,
            "lastStatus": self.init_default_attr,
            "launchType": self.init_default_attr,
            "memory": self.init_default_attr,
            "overrides": self.init_default_attr,
            "pullStartedAt": self.init_default_attr,
            "pullStoppedAt": self.init_default_attr,
            "startedAt": self.init_default_attr,
            "startedBy": self.init_default_attr,
            "tags": self.init_default_attr,
            "taskDefinitionArn": self.init_default_attr,
            "version": self.init_default_attr,
            "capacityProviderName": self.init_default_attr,
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

    @property
    def region(self):
        if self._region is not None:
            return self._region

        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value

    def get_status(self):
        raise NotImplementedError()
        if self.status is None:
            return self.Status.ACTIVE
        elif self.status == "Delete in progress":
            return self.Status.DELETING
        else:
            raise NotImplementedError(self.status)

    class Status(Enum):
        ACTIVE = 0
        DELETING = 1
