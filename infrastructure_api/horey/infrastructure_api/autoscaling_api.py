"""
Standard autoscaling maintainer.

"""

from horey.h_logger import get_logger

from horey.infrastructure_api.autoscaling_api_configuration_policy import AutoscalingAPIConfigurationPolicy
from horey.infrastructure_api.environment_api import EnvironmentAPI
from horey.aws_api.aws_services_entities.application_auto_scaling_scalable_target import \
    ApplicationAutoScalingScalableTarget
from horey.aws_api.aws_services_entities.application_auto_scaling_policy import ApplicationAutoScalingPolicy

logger = get_logger()


class AutoscalingAPI:
    """
    Manage Autoscaling.

    """

    def __init__(self, configuration: AutoscalingAPIConfigurationPolicy, environment_api: EnvironmentAPI):
        self.configuration = configuration
        self.environment_api = environment_api

    def provision_sqs_policy(self, ecs_api):
        breakpoint()

    def provision_application_autoscaling_policy(self, policy_name, target_value, predefind_metric_type=None,
                                                 customized_metric_specificationis=None):
        """
        Scales ecs-service's count based ram monitoring

        :return:
        """

        policy = ApplicationAutoScalingPolicy({})
        policy.region = self.environment_api.region
        policy.service_namespace = "ecs"
        policy.name = policy_name
        policy.resource_id = self.configuration.auto_scaling_resource_id
        policy.scalable_dimension = "ecs:service:DesiredCount"
        policy.policy_type = "TargetTrackingScaling"

        policy.target_tracking_scaling_policy_configuration = {
            "TargetValue": target_value,
            "ScaleOutCooldown": 60,
            "ScaleInCooldown": 300,
            "DisableScaleIn": False
        }

        if predefind_metric_type is not None:
            policy.target_tracking_scaling_policy_configuration["PredefinedMetricSpecification"] = {
                "PredefinedMetricType": predefind_metric_type
            }
        elif customized_metric_specificationis is not None:
            policy.target_tracking_scaling_policy_configuration["CustomizedMetricSpecification"] = \
                customized_metric_specificationis

        self.environment_api.aws_api.provision_application_auto_scaling_policy(policy)

    def provision_application_autoscaling_scalable_target(self):
        """
        Target is the application-autoscaling element representing ecs service to be monitored.

        :return:
        """

        # todo: cleanup report dead deregister dead scalable targets.

        target = ApplicationAutoScalingScalableTarget({})
        target.service_namespace = "ecs"
        target.region = self.environment_api.region
        target.resource_id = self.configuration.auto_scaling_resource_id
        target.scalable_dimension = "ecs:service:DesiredCount"
        target.min_capacity = self.configuration.autoscaling_min_capacity
        target.max_capacity = self.configuration.autoscaling_max_capacity
        target.role_arn = f"arn:aws:iam::{self.environment_api.aws_api.ecs_client.account_id}:role/aws-service-role/ecs.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_ECSService"
        target.suspended_state = {
            "DynamicScalingInSuspended": False,
            "DynamicScalingOutSuspended": False,
            "ScheduledScalingSuspended": False
        }
        target.tags = {tag["Key"]: tag["Value"] for tag in self.environment_api.get_tags_with_name(f"{target.resource_id}/{target.scalable_dimension}")}
        self.environment_api.aws_api.provision_application_auto_scaling_scalable_target(target)
