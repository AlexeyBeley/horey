"""
AWS ECS Task representation
"""
from enum import Enum

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class ECSTask(AwsObject):
    """
    AWS Task class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.cluster_arn = None
        self.last_status = None

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
            "platformVersion": self.init_default_attr,
            "platformFamily": self.init_default_attr,
            "ephemeralStorage": self.init_default_attr,
            "stoppingAt": self.init_default_attr,
            "stoppedReason": self.init_default_attr,
            "stoppedAt": self.init_default_attr,
            "stopCode": self.init_default_attr,
            "executionStoppedAt": self.init_default_attr,
            "fargateEphemeralStorage": self.init_default_attr,
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
        Get state.

        """

        mapping = dict(self.State.__members__)
        return mapping[self.last_status]

    class State(Enum):
        """
        Volume state.

        """

        RUNNING = "RUNNING"
        PROVISIONING = "PROVISIONING"
        PENDING = "PENDING"
        ACTIVATING = "ACTIVATING"
        FAILED = "FAILED"
        DEACTIVATING = "DEACTIVATING"
        STOPPING = "STOPPING"
        DEPROVISIONING = "DEPROVISIONING"
        STOPPED = "STOPPED"
