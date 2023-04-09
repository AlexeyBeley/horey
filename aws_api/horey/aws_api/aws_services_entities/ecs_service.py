"""
AWS Lambda representation
"""

from enum import Enum
from horey.aws_api.aws_services_entities.aws_object import AwsObject


# pylint: disable=too-many-instance-attributes
class ECSService(AwsObject):
    """
    AWS ECSService class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None
        self.propagate_tags = None
        self.service_registries = None
        self.role_arn = None
        self.load_balancers = None
        self.cluster_arn = None
        self.task_definition = None

        self.deployment_configuration = None
        self.placement_strategy = None
        self.health_check_grace_period_seconds = None
        self.enable_execute_command = None
        self.status = None
        self.desired_count = None

        self.launch_type = None
        self.scheduling_strategy = None
        self.enable_ecs_managed_tags = None
        self.arn = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "serviceArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
            "serviceName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "clusterArn": self.init_default_attr,
            "loadBalancers": self.init_default_attr,
            "serviceRegistries": self.init_default_attr,
            "desiredCount": self.init_default_attr,
            "runningCount": self.init_default_attr,
            "pendingCount": self.init_default_attr,
            "capacityProviderStrategy": self.init_default_attr,
            "taskDefinition": self.init_default_attr,
            "deploymentConfiguration": self.init_default_attr,
            "deployments": self.init_default_attr,
            "roleArn": self.init_default_attr,
            "events": self.init_default_attr,
            "createdAt": self.init_default_attr,
            "placementConstraints": self.init_default_attr,
            "placementStrategy": self.init_default_attr,
            "healthCheckGracePeriodSeconds": self.init_default_attr,
            "schedulingStrategy": self.init_default_attr,
            "createdBy": self.init_default_attr,
            "enableECSManagedTags": self.init_default_attr,
            "propagateTags": self.init_default_attr,
            "enableExecuteCommand": self.init_default_attr,
            "status": self.init_default_attr,
            "launchType": self.init_default_attr,
            "tags": self.init_default_attr,
            "deploymentController": self.init_default_attr,
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

    def update_from_raw_response(self, dict_src):
        """
        Standard.

        :param dict_src:
        :return:
        """

        init_options = {
            "serviceArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
            "serviceName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "clusterArn": self.init_default_attr,
            "loadBalancers": self.init_default_attr,
            "serviceRegistries": self.init_default_attr,
            "desiredCount": self.init_default_attr,
            "runningCount": self.init_default_attr,
            "pendingCount": self.init_default_attr,
            "capacityProviderStrategy": self.init_default_attr,
            "taskDefinition": self.init_default_attr,
            "deploymentConfiguration": self.init_default_attr,
            "deployments": self.init_default_attr,
            "roleArn": self.init_default_attr,
            "events": self.init_default_attr,
            "createdAt": self.init_default_attr,
            "placementConstraints": self.init_default_attr,
            "placementStrategy": self.init_default_attr,
            "healthCheckGracePeriodSeconds": self.init_default_attr,
            "schedulingStrategy": self.init_default_attr,
            "createdBy": self.init_default_attr,
            "enableECSManagedTags": self.init_default_attr,
            "propagateTags": self.init_default_attr,
            "enableExecuteCommand": self.init_default_attr,
            "status": self.init_default_attr,
            "launchType": self.init_default_attr,
            "tags": self.init_default_attr,
            "deploymentController": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard.

        :return:
        """

        request = {"serviceName": self.name, "cluster": self.cluster_arn, "taskDefinition": self.task_definition}

        if self.load_balancers is not None:
            request["loadBalancers"] = self.load_balancers
            request[
                "healthCheckGracePeriodSeconds"
            ] = self.health_check_grace_period_seconds
            if self.role_arn is not None:
                request["role"] = self.role_arn

        if self.service_registries is not None:
            request["serviceRegistries"] = self.service_registries

        request["desiredCount"] = self.desired_count

        request["launchType"] = self.launch_type

        request["deploymentConfiguration"] = self.deployment_configuration
        request["placementStrategy"] = self.placement_strategy
        request["schedulingStrategy"] = self.scheduling_strategy
        request["enableECSManagedTags"] = self.enable_ecs_managed_tags
        if self.propagate_tags is not None:
            request["propagateTags"] = self.propagate_tags
        request["enableExecuteCommand"] = self.enable_execute_command

        request["tags"] = self.tags
        return request

    def generate_dispose_request(self, cluster):
        """
        Standard.

        :param cluster:
        :return:
        """

        request = {"service": self.name, "cluster": cluster.name, "force": True}
        return request

    def generate_update_request(self):
        """
        Standard.

        :return:
        """

        request = {"service": self.name, "cluster": self.cluster_arn, "taskDefinition": self.task_definition,
                   "desiredCount": self.desired_count, "deploymentConfiguration": self.deployment_configuration,
                   "placementStrategy": self.placement_strategy}
        if self.load_balancers is not None:
            request[
                "healthCheckGracePeriodSeconds"
            ] = self.health_check_grace_period_seconds
        request["enableExecuteCommand"] = self.enable_execute_command

        return request

    def get_status(self):
        """

        :return:
        """
        return {
            enum_value.value: enum_value
            for _, enum_value in self.Status.__members__.items()
        }[self.status]

    class Status(Enum):
        """
        Standard.
        """
        ACTIVE = "ACTIVE"
        DRAINING = "DRAINING"
        INACTIVE = "INACTIVE"

    class Deployment(AwsObject):
        """
        Single deployment.

        """

        def __init__(self, dict_src, from_cache=False):
            super().__init__(dict_src)
            self._region = None
            self.status = None

            if from_cache:
                self._init_object_from_cache(dict_src)
                return

            init_options = {
                "id": self.init_default_attr,
                "status": self.init_default_attr,
                "taskDefinition": self.init_default_attr,
                "desiredCount": self.init_default_attr,
                "pendingCount": self.init_default_attr,
                "runningCount": self.init_default_attr,
                "failedTasks": self.init_default_attr,
                "createdAt": self.init_default_attr,
                "updatedAt": self.init_default_attr,
                "launchType": self.init_default_attr,
                "rolloutState": self.init_default_attr,
                "rolloutStateReason": self.init_default_attr,
            }

            self.init_attrs(dict_src, init_options, raise_on_no_option=True)

        def _init_object_from_cache(self, dict_src):
            """
            Init from cache

            :param dict_src:
            :return:
            """

            options = {}
            self._init_from_cache(dict_src, options)
