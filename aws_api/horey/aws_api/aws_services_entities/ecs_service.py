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
        self.capacity_provider_strategy = None
        self.force_new_deployment = None
        self.service_connect_configuration = None
        self.volume_configurations = None
        self.placement_constraints = None
        self.platform_version = None

        self.launch_type = None
        self.scheduling_strategy = None
        self.enable_ecs_managed_tags = None
        self.deployments = []
        self.network_configuration = None
        self.request_key_to_attribute_mapping = {"cluster": "cluster_arn", "service": "name"}

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        self.update_from_raw_response(dict_src)

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
            "networkConfiguration": self.init_default_attr,
            "platformFamily": self.init_default_attr,
            "platformVersion": self.init_default_attr,
            "availabilityZoneRebalancing": self.init_default_attr,
            "resourceManagementType": self.init_default_attr,
            "currentServiceRevisions": self.init_default_attr,
            "currentServiceDeployment": self.init_default_attr,
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

        request["desiredCount"] = self.desired_count

        request["launchType"] = self.launch_type

        request["schedulingStrategy"] = self.scheduling_strategy
        request["enableECSManagedTags"] = self.enable_ecs_managed_tags
        request["enableExecuteCommand"] = self.enable_execute_command

        request["tags"] = self.tags
        self.extend_request_with_optional_parameters(request,
                                                     ["placementStrategy", "propagateTags", "networkConfiguration",
                                                      "serviceRegistries"])

        return request

    def generate_dispose_request(self, cluster):
        """
        Standard.

        :param cluster:
        :return:
        """

        if not cluster.name:
            raise ValueError("Cluster name was not set")

        request = {"service": self.name, "cluster": cluster.name, "force": True}
        return request

    def generate_update_request(self, desired_state):
        """
        Standard.
        request = {"service": self.name, "cluster": self.cluster_arn, "taskDefinition": self.task_definition,
                   "desiredCount": self.desired_count}
        if self.load_balancers is not None:
            request[
                "healthCheckGracePeriodSeconds"
            ] = self.health_check_grace_period_seconds
        request["enableExecuteCommand"] = self.enable_execute_command
        self.extend_request_with_optional_parameters(request,
                                                     ["placementStrategy", "propagateTags", "networkConfiguration",
                                                      "serviceRegistries", "deploymentConfiguration"])

        return request
        :return:
        """

        required = ["service", "cluster"]
        optional = ["taskDefinition",
                    "desiredCount",
                    "taskDefinition",
                    "healthCheckGracePeriodSeconds",
                    "placementStrategy",
                    "propagateTags",
                    "networkConfiguration",
                    "serviceRegistries",
                    "deploymentConfiguration",
                    "capacityProviderStrategy",
                    "placementConstraints",
                    "platformVersion",
                    "forceNewDeployment",
                    "enableExecuteCommand",
                    "enableECSManagedTags",
                    "loadBalancers",
                    "serviceConnectConfiguration",
                    "volumeConfigurations"]

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
            self.status = None
            self.rollout_state = None
            self.desired_count = None
            self.running_count = None

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
                "networkConfiguration": self.init_default_attr,
                "platformFamily": self.init_default_attr,
                "platformVersion": self.init_default_attr
            }

            self.init_attrs(dict_src, init_options, raise_on_no_option=False)

        def _init_object_from_cache(self, dict_src):
            """
            Init from cache

            :param dict_src:
            :return:
            """

            options = {}
            self._init_from_cache(dict_src, options)
