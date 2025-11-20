"""
Standard ECS maintainer.

"""
import json
import os
import pathlib
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from horey.h_logger import get_logger

from horey.aws_api.aws_services_entities.ecr_image import ECRImage
from horey.aws_api.aws_services_entities.ecr_repository import ECRRepository
from horey.aws_api.aws_services_entities.ecs_task import ECSTask
from horey.aws_api.base_entities.region import Region
from horey.infrastructure_api.alerts_api import AlertsAPI
from horey.infrastructure_api.alerts_api_configuration_policy import AlertsAPIConfigurationPolicy
from horey.infrastructure_api.cloudwatch_api_configuration_policy import CloudwatchAPIConfigurationPolicy
from horey.infrastructure_api.aws_iam_api_configuration_policy import AWSIAMAPIConfigurationPolicy
from horey.infrastructure_api.aws_iam_api import AWSIAMAPI
from horey.infrastructure_api.ecs_api_configuration_policy import ECSAPIConfigurationPolicy
from horey.infrastructure_api.environment_api import EnvironmentAPI
from horey.infrastructure_api.cloudwatch_api import CloudwatchAPI
from horey.aws_api.aws_services_entities.application_auto_scaling_scalable_target import \
    ApplicationAutoScalingScalableTarget
from horey.aws_api.aws_services_entities.application_auto_scaling_policy import ApplicationAutoScalingPolicy
from horey.aws_api.aws_services_entities.event_bridge_rule import EventBridgeRule
from horey.aws_api.aws_services_entities.event_bridge_target import EventBridgeTarget
from horey.aws_api.aws_services_entities.ecs_cluster import ECSCluster

logger = get_logger()


class ECSAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration: ECSAPIConfigurationPolicy, environment_api: EnvironmentAPI):
        self.configuration = configuration
        self.environment_api = environment_api
        self._ecr_repository = None
        self._ecr_images = None
        self._alerts_api = None
        self._cloudwatch_api = None
        self._aws_iam_api = None
        self.loadbalancer_api = None
        self.dns_api = None
        self.loadbalancer_dns_api_pairs = None

        try:
            assert self.configuration.cluster_name
        except self.configuration.UndefinedValueError:
            self.configuration.cluster_name = f"cluster-{self.environment_api.configuration.project_name_abbr}-{self.environment_api.configuration.environment_level}-{self.environment_api.configuration.environment_name}"

        try:
            assert self.configuration.ecr_repository_region
        except self.configuration.UndefinedValueError:
            self.configuration.ecr_repository_region = self.environment_api.configuration.region

        try:
            assert self.configuration.ecs_task_role_name
        except self.configuration.UndefinedValueError:
            self.configuration.ecs_task_role_name = f"role_{self.environment_api.configuration.environment_level}_" \
                                                    f"{self.environment_api.configuration.project_name_abbr}_{self.configuration.service_name}_task"

        try:
            assert self.configuration.ecs_task_execution_role_name
        except self.configuration.UndefinedValueError:
            self.configuration.ecs_task_execution_role_name = f"role_{self.environment_api.configuration.environment_level}_" \
                                                    f"{self.environment_api.configuration.project_name_abbr}_{self.configuration.service_name}_exec"

    @property
    def ecr_repository(self):
        """
        Find once

        :return:
        """

        if self._ecr_repository is None:
            self.environment_api.aws_api.ecr_client.clear_cache(ECRRepository)
            src_ecr_repositories = self.environment_api.aws_api.ecr_client.get_region_repositories(
                region=Region.get_region(self.configuration.ecr_repository_region),
                repository_names=[
                    self.configuration.ecr_repository_name])
            if len(src_ecr_repositories) != 1:
                raise RuntimeError(f"Can not find repository {self.configuration.ecr_repository_name}")
            self._ecr_repository = src_ecr_repositories[0]
        return self._ecr_repository

    @property
    def ecr_images(self):
        """
        Init once

        :return:
        """
        if self._ecr_images is None:
            self.environment_api.aws_api.ecr_client.clear_cache(ECRImage)
            self._ecr_images = self.environment_api.aws_api.ecr_client.get_repository_images(self.ecr_repository)
        return self._ecr_images

    def set_api(self, loadbalancer_api=None, dns_api=None, cloudwatch_api=None, loadbalancer_dns_api_pairs=None):
        """
        Standard.

        :param loadbalancer_dns_api_pairs: Load balancer, with DNS_API pair - the DNS Api used for specific LB.
        Useful when you have 2 addresses for the service - internal and external.

        :param loadbalancer_api:
        :param dns_api:
        :return:
        """

        if loadbalancer_dns_api_pairs:
            # todo: fix DNS rules validation.
            breakpoint()
            if len(self.configuration.container_definition_port_mappings) != 1:
                raise NotImplementedError("Need to implement dynamic test that loadbalancer_api configuration has the"
                                          " port set explicitly")

            container_port = self.configuration.container_definition_port_mappings[0]["containerPort"]
            for lb_api, _ in loadbalancer_dns_api_pairs:
                if lb_api.configuration.target_group_port != self.configuration.container_definition_port_mappings[0][
                    "containerPort"]:
                    raise NotImplementedError(f"loadbalancer_api for LB: '{lb_api.configuration.load_balancer_name}'"
                                              f" configuration has no {container_port} port set for 'target_group_port'")

            if loadbalancer_api or dns_api:
                raise NotImplementedError(
                    "You can not both declare loadbalancer_dns_apis_pairs and either lb_api or dns_api")

            for loadbalancer_api, _ in loadbalancer_dns_api_pairs:
                assert loadbalancer_api.configuration.load_balancer_name
                assert loadbalancer_api.configuration.target_group_name

            self.loadbalancer_dns_api_pairs = loadbalancer_dns_api_pairs

        if loadbalancer_api:
            self.loadbalancer_api = loadbalancer_api
            try:
                self.loadbalancer_api.configuration.target_group_name
            except self.loadbalancer_api.configuration.UndefinedValueError:
                self.loadbalancer_api.configuration.target_group_name = f"tg-cluster-{self.environment_api.configuration.project_name_abbr}"\
                                                                        f"-{self.environment_api.configuration.environment_level_abbr}"\
                                                                        f"-{self.environment_api.configuration.environment_name_abbr}"\
                                                                        f"-{self.configuration.service_name}"

            try:
                self.loadbalancer_api.configuration.load_balancer_name
            except self.loadbalancer_api.configuration.UndefinedValueError:
                self.loadbalancer_api.configuration.load_balancer_name = f"lb-cluster-{self.environment_api.configuration.project_name_abbr}" \
                                                                        f"-{self.environment_api.configuration.environment_level_abbr}" \
                                                                        f"-{self.environment_api.configuration.environment_name_abbr}"

            if len(self.configuration.container_definition_port_mappings) != 1:
                raise NotImplementedError("Need to implement dynamic test that loadbalancer_api configuration has the"
                                          " port set explicitly")
            self.loadbalancer_api.configuration.target_group_port = \
            self.configuration.container_definition_port_mappings[0]["containerPort"]
            if self.dns_api:
                raise NotImplementedError("todo: Validate the DNS addresses in DNS are the same as in load balancer.")

        if dns_api:
            self.dns_api = dns_api
            if self.dns_api.configuration._lowest_domain_label is None:
                # todo: remove ng
                self.dns_api.configuration.lowest_domain_label = self.configuration.service_name
            if self.loadbalancer_api:
                try:
                    self.loadbalancer_api.configuration.rule_conditions
                except self.loadbalancer_api.configuration.UndefinedValueError:
                    self.loadbalancer_api.configuration.rule_conditions = [
                        {
                            "Field": "host-header",
                            "HostHeaderConfig": {
                                "Values": [self.dns_api.configuration.dns_address]
                            }
                        }
                    ]

                try:
                    self.loadbalancer_api.configuration.certificates_domain_names
                except self.loadbalancer_api.configuration.UndefinedValueError:
                    self.loadbalancer_api.configuration.certificates_domain_names = \
                        ["*." + self.dns_api.configuration.dns_address.split(".", maxsplit=1)[1]]

                if self.dns_api.configuration.dns_address not in self.loadbalancer_api.configuration.certificates_domain_names and \
                        "*." + self.dns_api.configuration.dns_address.split(".", maxsplit=1)[1] not in \
                        self.loadbalancer_api.configuration.certificates_domain_names:
                    raise NotImplementedError(
                        f"Check why service DNS {self.dns_api.configuration.dns_address} is not among load balancer DNS addresses: {self.loadbalancer_api.configuration.certificates_domain_names:}")

        if cloudwatch_api:
            if not cloudwatch_api.configuration.log_group_name:
                raise ValueError("Log group name not set")
            self.cloudwatch_api = cloudwatch_api

        if self.dns_api and self.loadbalancer_api:

            try:
                self.loadbalancer_api.configuration.scheme
            except self.loadbalancer_api.configuration.UndefinedValueError:
                if self.dns_api.hosted_zone.config["PrivateZone"]:
                    self.loadbalancer_api.configuration.scheme = "internal"
                else:
                    self.loadbalancer_api.configuration.scheme = "internet-facing"

            try:
                self.loadbalancer_api.configuration.security_groups
            except self.loadbalancer_api.configuration.UndefinedValueError:
                if self.loadbalancer_api.configuration.scheme == "internet-facing":
                    self.loadbalancer_api.configuration.security_groups = [f"sg_lb-public-{self.configuration.slug.replace('_', '-')}"]
                else:
                    self.loadbalancer_api.configuration.security_groups = [f"sg_lb-{self.configuration.slug.replace('_', '-')}"]

    def validate_input(self):
        """
        Check service or scheduled tasks were defined correctly
        :return:
        """

        if self.configuration.schedule_expression:
            if self.configuration.provision_service:
                raise ValueError("Can not accept both scheduled expression and service_name")

            if not self.configuration.provision_cron:
                raise ValueError("If scheduled expression provided cron_name must be provided")

            if self.dns_api or self.loadbalancer_dns_api_pairs or self.loadbalancer_api:
                raise ValueError("Cron can not have DNS or LoadBalancer")

        if (
                self.configuration.provision_service or self.configuration.provision_cron or self.configuration.provision_adhoc_task) and self.configuration.cluster_name is None:
            raise ValueError("If scheduled expression provided cluster name must be provided")

    def provision(self):
        """
        Provision ECS infrastructure.

        :return:
        """
        # todo: cleanup ecs service Deployment circuit breaker
        # todo: cleanup ecs service: CloudWatch alarms for deployment
        # todo: cleanup ecs scheduled task reduce ecsEventsRole permissions to only allow passing TaskRole and Execution role
        self.validate_input()

        self.environment_api.aws_api.ecr_client.clear_cache(None, all_cache=True)
        self.provision_ecr_repository()

        if not self.configuration.provision_service and not self.configuration.provision_cron:
            return True

        self.provision_cluster()

        self.cloudwatch_api.provision()
        # todo: move to environment_api
        # self.provision_monitoring()
        self.provision_task_role()
        self.provision_execution_role()

        if self.loadbalancer_api:
            self.provision_lb_security_groups()
            self.loadbalancer_api.provision()
            self.provision_lb_facing_security_group()

        if self.configuration.provision_service:
            self.update()
        elif self.configuration.provision_cron:
            task_definition = self.update()
            events_rule = self.provision_events_rule()
            self.provision_events_rule_target(events_rule, task_definition)
        else:
            raise ValueError("Unknown state")

        if self.dns_api:
            self.dns_api.configuration.dns_target = self.loadbalancer_api.get_loadbalancer().dns_name
            self.dns_api.provision()

        elif self.loadbalancer_dns_api_pairs:
            breakpoint()
            for loadbalancer_api, dns_api in self.loadbalancer_dns_api_pairs:
                dns_api.configuration.dns_target = loadbalancer_api.get_loadbalancer().dns_name
                dns_api.provision()

        if self.configuration.provision_service:
            self.provision_autoscaling()

        return True

    def provision_cluster(self):
        """
        Provision the ECS cluster for this env.

        :return:
        """

        cluster = ECSCluster({})
        cluster.settings = [
            {
                "name": "containerInsights",
                "value": "disabled"
            }
        ]

        cluster.name = self.configuration.cluster_name
        cluster.region = self.environment_api.region
        cluster.tags = [{key.lower(): value for key, value in dict_tag.items()} for dict_tag in self.environment_api.get_tags_with_name(cluster.name)]
        cluster.configuration = {}

        self.environment_api.aws_api.provision_ecs_cluster(cluster)
        return cluster

    def provision_lb_security_groups(self):
        """
        Provision LB security group.

        :return:
        """

        for sg_name in self.loadbalancer_api.configuration.security_groups:
            self.environment_api.provision_security_group(sg_name)

    def provision_lb_facing_security_group(self):
        """
        Provision LB security group.

        :return:
        """

        if not self.loadbalancer_api:
            raise NotImplementedError("No lb api set")
        lb_groups = self.environment_api.get_security_groups(self.loadbalancer_api.configuration.security_groups)
        ip_permissions = [
            {
                "IpProtocol": "tcp",
                "FromPort": self.loadbalancer_api.configuration.target_group_port,
                "ToPort": self.loadbalancer_api.configuration.target_group_port,
                "UserIdGroupPairs": [
                    {
                        "GroupId": lb_group.id,
                        "UserId": self.environment_api.aws_api.ecr_client.account_id,
                        "Description": f"From {lb_group.name}"
                    } for lb_group in lb_groups
                ]
            }
        ]
        return self.environment_api.provision_security_group(self.configuration.lb_facing_security_group_name,
                                                             ip_permissions)

    def provision_autoscaling(self):
        """
        Provision application-autoscaling services' elements.

        :return:
        """

        if self.configuration.autoscaling_max_capacity == 1:
            return True

        self.provision_application_autoscaling_scalable_target()
        self.provision_application_autoscaling_policies()
        return True

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

    def provision_application_autoscaling_policies(self):
        """
        Policy is the application-autoscaling element responsible for scaling management.
        It implicitly creates cloudwatch alarm, thus there are ugly alarms.
        You can see the policy in ecs/service/autoscaling tab.

        :return:
        """
        # todo: cleanup report dead deregister dead scalable targets policies

        self.provision_application_autoscaling_policy(self.configuration.autoscaling_ram_policy_name,
                                                      self.configuration.autoscaling_ram_target_value,
                                                      predefind_metric_type="ECSServiceAverageMemoryUtilization")
        self.provision_application_autoscaling_policy(self.configuration.autoscaling_cpu_policy_name,
                                                      self.configuration.autoscaling_cpu_target_value,
                                                      predefind_metric_type="ECSServiceAverageCPUUtilization"
                                                      )

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

    def environment_variables_callback(self):
        """
        Made for async generation.

        :return:
        """

        return []

    def task_role_inline_policies_callback(self):
        """
        Made for async generation.

        :return:
        """

        return []

    def prepare_container_build_directory(self, source_code_dir, commit_id, build_number):
        """
        Copy source code to tmp dir.

        :param build_number:
        :param commit_id:
        :param source_code_dir:
        :return:
        """
        source_code_dir_tmp = Path("/tmp/ecs_api_build_temp_dirs") / str(uuid.uuid4())
        source_code_dir_tmp.parent.mkdir(exist_ok=True)

        def ignore_git(_, file_names):
            return [".git", ".gitmodules", ".idea"] if ".git" in file_names else []

        shutil.copytree(source_code_dir, source_code_dir_tmp, ignore=ignore_git)

        with open(source_code_dir_tmp / "commit_and_build.json", "w", encoding="utf-8") as file_handler:
            json.dump({"commit": commit_id, "build": str(build_number)}, file_handler)
        return self.prepare_container_build_directory_callback(source_code_dir_tmp)

    def prepare_container_build_directory_callback(self, dir_path: pathlib.Path):
        """
        Echo.

        :param dir_path:
        :return:
        """

        return dir_path

    def update(self):
        """

        :return:
        """

        self.validate_input()
        ecr_image_tag = self.get_build_tag()
        ecs_task_definition = self.provision_ecs_task_definition(ecr_image_tag)

        if self.configuration.provision_cron:
            return ecs_task_definition

        if not self.configuration.provision_service:
            raise ValueError("Unknown status")

        return self.provision_ecs_service(ecs_task_definition)

    def provision_ecs_task_definition(self, ecr_image_tag):
        """
        Provision task definition.

        :return:
        """

        task_definition = self.environment_api.provision_ecs_fargate_task_definition(
            task_definition_family=self.configuration.family,
            contaner_name=self.configuration.container_name,
            ecr_image_id=ecr_image_tag,
            port_mappings=self.configuration.container_definition_port_mappings,
            cloudwatch_log_group_name=self.configuration.cloudwatch_log_group_name,
            entry_point=self.configuration.task_definition_entry_point,
            environ_values=self.environment_variables_callback(),
            requires_compatibilities=self.configuration.requires_compatibilities,
            network_mode=self.configuration.network_mode,
            volumes=self.configuration.task_definition_volumes,
            mount_points=self.configuration.task_definition_mount_points,
            ecs_task_definition_cpu_reservation=self.configuration.ecs_task_definition_cpu_reservation,
            ecs_task_definition_memory_reservation=self.configuration.ecs_task_definition_memory_reservation,
            ecs_task_role_name=self.configuration.ecs_task_role_name,
            ecs_task_execution_role_name=self.configuration.ecs_task_execution_role_name,
            task_definition_cpu_architecture=self.configuration.task_definition_cpu_architecture
        )
        return task_definition

    def provision_ecs_service(self, ecs_task_definition):
        """
        Provision component's ECS service.

        :return:
        """

        try:
            security_groups = self.configuration.security_groups
        except self.configuration.UndefinedValueError:
            security_groups = []

        if self.loadbalancer_api:
            security_groups.append(self.configuration.lb_facing_security_group_name)
            target_groups = [self.loadbalancer_api.get_targetgroup()]
        elif self.loadbalancer_dns_api_pairs:
            target_groups = [loadbalancer_api.get_targetgroup() for loadbalancer_api in self.loadbalancer_dns_api_pairs]
        else:
            target_groups = []

        security_groups = self.environment_api.get_security_groups(security_groups)

        load_blanacer_dicts = [{
            "targetGroupArn": target_group.arn,
            "containerName": self.configuration.container_name,
            "containerPort": self.configuration.container_definition_port_mappings[0]["containerPort"]
        } for target_group in target_groups
        ]

        if self.configuration.service_registry_arn:
            service_registry_dicts = [{
                "registryArn": self.configuration.service_registry_arn,
                "containerName": self.configuration.container_name,
                "containerPort": self.configuration.container_definition_port_mappings[0]["containerPort"]
            }]
        else:
            service_registry_dicts = None

        return self.environment_api.provision_ecs_service(self.configuration.cluster_name,
                                                          ecs_task_definition,
                                                          td_desired_count=self.configuration.task_definition_desired_count,
                                                          launch_type=self.configuration.launch_type,
                                                          network_configuration={
                                                              "awsvpcConfiguration": {
                                                                  "subnets": [subnet.id for subnet in
                                                                              self.environment_api.private_subnets],
                                                                  "securityGroups": [security_group.id for
                                                                                     security_group in
                                                                                     security_groups],
                                                                  "assignPublicIp": "DISABLED"
                                                              }
                                                          },
                                                          service_name=self.configuration.service_name,
                                                          container_name=self.configuration.container_name,
                                                          kill_old_containers=self.configuration.kill_old_containers,
                                                          load_blanacer_dicts=load_blanacer_dicts,
                                                          service_registry_dicts=service_registry_dicts
                                                          )

    def provision_ecr_repository(self):
        """
        Create or update the ECR repo

        :return:
        """

        repo = ECRRepository({})
        repo.region = Region.get_region(self.configuration.ecr_repository_region)
        repo.name = self.configuration.ecr_repository_name
        if self.configuration.ecr_repository_policy_text:
            # todo: generate policy to permit only access from relevant services: AWS Lambda / ECS / EKS etc
            repo.policy_text = self.configuration.ecr_repository_policy_text
        repo.tags = self.environment_api.get_tags_with_name(repo.name)

        repo.tags.append({
            "Key": self.configuration.infrastructure_update_time_tag,
            "Value": datetime.now().strftime("%Y_%m_%d_%H_%M")
        })

        self.environment_api.aws_api.provision_ecr_repository(repo)
        return repo

    @staticmethod
    def tiny_dockerfile(container_build_dir_path):
        """
        700K docker image.

        :return:
        """
        os.makedirs(container_build_dir_path, exist_ok=True)
        with open(os.path.join(container_build_dir_path, "Dockerfile"), "w", encoding="utf-8") as fh:
            fh.writelines(["FROM k8s.gcr.io/pause\n"])

    def get_build_tag(self, nocache=False):
        """
        Build if needed.
        Upload if needed.
        Download if needed.

        :param nocache:
        :return:
        """

        ecr_image = self.fetch_latest_artifact_metadata()
        build_number = ecr_image.build_number if ecr_image is not None else -1
        repo_uri = f"{self.environment_api.aws_api.ecs_client.account_id}.dkr.ecr.{self.configuration.ecr_repository_region}.amazonaws.com/{self.configuration.ecr_repository_name}"

        if image_tag := self.build_ecr_image_from_source_code(repo_uri, build_number, nocache):
            self._ecr_images = None
            max_build_ecr_image = self.fetch_latest_artifact_metadata()
            if image_tag[len(repo_uri + "1"):] not in max_build_ecr_image.image_tags:
                raise RuntimeError(
                    f"Uploaded image {image_tag} is not viewable locally. Max version locally: {max_build_ecr_image.image_tags}")
            return image_tag

        if ecr_image is None:
            raise RuntimeError(f"Images store '{repo_uri}' is empty yet, use branch_name to build an image")

        image_tag_raw = ecr_image.image_tags[-1]
        image_tag = f"{repo_uri}:{image_tag_raw}"

        return image_tag

    def build_ecr_image_from_source_code(self, repo_uri, build_number, nocache):
        """
        Build from repo.

        :param repo_uri:
        :param build_number:
        :param nocache:
        :return:
        """

        if self.environment_api.git_api is None:
            return None

        if self.environment_api.git_api.configuration.branch_name is None:
            return None

        if not self.environment_api.git_api.checkout_remote():
            raise RuntimeError(
                f"Was not able to checkout branch: {self.environment_api.git_api.configuration.branch_name}")

        commit_id = self.environment_api.git_api.get_commit_id()

        tags = [f"{repo_uri}:build_{build_number + 1}-commit_{commit_id}"]

        build_dir_path = self.prepare_container_build_directory(
            self.environment_api.git_api.configuration.directory_path, commit_id, build_number)

        image = self.environment_api.build_and_upload_ecr_image(build_dir_path, tags, nocache,
                                                                buildargs=self.configuration.buildargs)
        assert tags[0] in image.tags
        return tags[0]

    @property
    def ecr_repo_uri(self):
        """
        Generate repo URI.

        :return:
        """

        return f"{self.environment_api.aws_api.ecs_client.account_id}.dkr.ecr.{self.configuration.ecr_repository_region}.amazonaws.com/{self.configuration.ecr_repository_name}"

    def fetch_latest_artifact_metadata(self):
        """
        From ECR

        :return:
        """

        for ecr_image in self.ecr_images:
            build_numbers = [int(build_subtag.split("_")[1]) for str_image_tag in ecr_image.image_tags for build_subtag
                             in
                             str_image_tag.split("-") if build_subtag.startswith("build_")]
            ecr_image.build_number = max(build_numbers)
        try:
            return max(self.ecr_images, key=lambda _image: _image.build_number)
        except ValueError as inst_error:
            if "iterable argument is empty" not in repr(inst_error) and "arg is an empty sequence" not in repr(
                    inst_error):
                raise
        return None

    def get_build_artifact(self):
        """
        Latest build image.

        :return:
        """

        max_build_ecr_image = self.fetch_latest_artifact_metadata()

        return self.environment_api.download_ecr_image(self.ecr_repo_uri, max_build_ecr_image.image_tags)

    @property
    def alerts_api(self):
        """
        Alerts api

        :return:
        """

        if self._alerts_api is None:
            alerts_api_configuration = AlertsAPIConfigurationPolicy()
            breakpoint()
            if "ecs_task" in self.configuration.ecs_task_role_name or "ecs-task" in self.configuration.ecs_task_role_name:
                alerts_api_configuration.lambda_role_name = self.configuration.ecs_task_role_name. \
                    replace("ecs_task", "has2"). \
                    replace("ecs-task", "has2")
                if alerts_api_configuration.lambda_role_name.count("has2") != 1:
                    raise ValueError(f"Expected single 'has2' in '{alerts_api_configuration.lambda_role_name}'")
            else:
                alerts_api_configuration.lambda_role_name = self.configuration.ecs_task_role_name + "-has2"

            alerts_api_configuration.lambda_name = f"has2-{self.configuration.slug}"
            alerts_api_configuration.horey_repo_path = os.path.join(
                self.environment_api.git_api.configuration.git_directory_path, "horey")

            self._alerts_api = AlertsAPI(alerts_api_configuration, self.environment_api)
        return self._alerts_api

    @property
    def cloudwatch_api(self):
        """
        Standard.

        :return:
        """
        if self._cloudwatch_api is None:
            config = CloudwatchAPIConfigurationPolicy()
            config.log_group_name = self.configuration.cloudwatch_log_group_name
            self._cloudwatch_api = CloudwatchAPI(configuration=config, environment_api=self.environment_api)

        return self._cloudwatch_api

    @cloudwatch_api.setter
    def cloudwatch_api(self, value):
        if not isinstance(value, CloudwatchAPI):
            raise ValueError(value)
        self._cloudwatch_api = value

    @property
    def aws_iam_api(self):
        """
        Standard

        :return:
        """

        if self._aws_iam_api is None:
            config = AWSIAMAPIConfigurationPolicy()
            self._aws_iam_api = AWSIAMAPI(configuration=config, environment_api=self.environment_api)
        return self._aws_iam_api

    def provision_monitoring(self):
        """
        Provision alert system and alerts.

        :return:
        """

        self.alerts_api.provision()
        self.alerts_api.provision_cloudwatch_logs_alarm(self.cloudwatch_api.configuration.log_group_name,
                                                        self.configuration.alerts_api_error_filter_text,
                                                        "error", None, dimensions=None,
                                                        alarm_description=None)

        return True

    def provision_task_role(self):
        """
        Provision role used by the task.

        :return:
        """

        if not self.configuration.provision_service and not self.configuration.provision_cron:
            return True

        policies = self.task_role_inline_policies_callback()
        assume_role_policy_document = json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ecs-tasks.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        })
        return self.aws_iam_api.provision_role(policies=policies, role_name=self.configuration.ecs_task_role_name,
                                               assume_role_policy=assume_role_policy_document)

    def provision_execution_role(self):
        """
        Role used by ECS service task running on the container instance to manage containers.

        :return:
        """

        if not self.configuration.provision_service and not self.configuration.provision_cron:
            return True

        assume_role_policy_document = json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ecs-tasks.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "ArnLike": {
                            "aws:SourceArn": f"arn:aws:ecs:{self.environment_api.configuration.region}:{self.environment_api.aws_api.ecs_client.account_id}:*"
                        },
                        "StringEquals": {
                            "aws:SourceAccount": self.environment_api.aws_api.ecs_client.account_id
                        }
                    }
                }
            ]
        })

        managed_policies_arns = ["arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"]
        return self.aws_iam_api.provision_role(managed_policies_arns=managed_policies_arns,
                                               role_name=self.configuration.ecs_task_execution_role_name,
                                               assume_role_policy=assume_role_policy_document,
                                               description="ECS task role used to control containers lifecycle")

    def provision_events_rule(self):
        """
        Event bridge rule - the trigger used to trigger the lambda each minute.

        :return:
        """

        rule = EventBridgeRule({})
        rule.name = self.configuration.event_bridge_rule_name
        rule.description = f"{self.configuration.cron_name} triggering rule"
        rule.region = self.environment_api.region
        rule.schedule_expression = self.configuration.schedule_expression
        rule.event_bus_name = "default"
        rule.state = "ENABLED"
        rule.tags = self.environment_api.get_tags_with_name(rule.name)

        self.environment_api.aws_api.provision_events_rule(rule)
        return rule

    def provision_events_rule_target(self, events_rule, task_definition):
        """
        Provision target to be triggered.

        :param events_rule:
        :param task_definition:
        :return:
        """

        security_groups = self.environment_api.get_security_groups(self.configuration.security_groups)

        target = EventBridgeTarget({})
        target.id = f"target-{self.configuration.cron_name}"
        target.arn = self.get_cluster().arn
        target.role_arn = f"arn:aws:iam::{self.environment_api.aws_api.ecr_client.account_id}:role/ecsEventsRole"
        target.ecs_parameters = {
            "TaskDefinitionArn": task_definition.arn,
            "TaskCount": 1,
            "LaunchType": "FARGATE",
            "NetworkConfiguration": {
                "awsvpcConfiguration": {
                    "Subnets": [subnet.id for subnet in self.environment_api.private_subnets],
                    "SecurityGroups": [security_group.id for security_group in security_groups],
                    "AssignPublicIp": "DISABLED"
                }
            },
            "PlatformVersion": "LATEST"
        }

        events_rule.targets = [target]
        self.environment_api.aws_api.provision_events_rule(events_rule)

    def get_cluster(self):
        """
        Standard.

        :return:
        """

        return self.environment_api.find_ecs_cluster(self.configuration.cluster_name)

    def tag_image(self, image, image_tags):
        """
        Tag local image.

        :param image:
        :param image_tags:
        :return:
        """

        self.environment_api.docker_api.tag_image(image, image_tags)

    def upload_ecr_image(self, image_tags):
        """
        Upload image tags.

        :return:
        """

        self.environment_api.upload_ecr_image(image_tags)

    def get_task_definition(self):
        """
        Geta latest task definition

        :return:
        """
        filters_req = {"familyPrefix": self.configuration.family, "status": "ACTIVE", "sort": "DESC"}
        for task_definition in self.environment_api.aws_api.ecs_client.yield_task_definitions(
                region=self.environment_api.region, filters_req=filters_req):
            breakpoint()
            return task_definition
        raise RuntimeError(f"Empty Family: {self.configuration.family}")

    def start_task(self, overrides=None):
        """
        Start latest TD of the task.

        :return:
        """

        self.validate_input()
        # task_definition = self.ecs_api.get_task_definition()

        dict_run_task_request = {
            "cluster": self.configuration.cluster_name,
            "taskDefinition": self.configuration.family,
            "launchType": "FARGATE",
            "networkConfiguration": {
                "awsvpcConfiguration": {
                    "subnets": [subnet.id for subnet in
                                self.environment_api.private_subnets],
                    "securityGroups": [sec_group.id for sec_group in self.environment_api.get_security_groups(self.configuration.security_groups)],
                    "assignPublicIp": "ENABLED",
                }
            },
        }
        if overrides:
            dict_run_task_request["overrides"] = overrides
        response = self.environment_api.aws_api.ecs_client.run_task(self.environment_api.region, dict_run_task_request)
        return ECSTask(response)

    def wait_for_task_to_finish(self, task):
        """
        Wait for the task to start and finish.

        :param task:
        :return:
        """
        #if not self.environment_api.aws_api.ecs_client.update_task_information(task):
        #    raise RuntimeError("Task was not found")
        task.id = self.configuration.adhoc_task_name
        self.environment_api.aws_api.ecs_client.wait_for_status(
            task,
            self.environment_api.aws_api.ecs_client.update_task_information,
            [task.State.RUNNING],
            [task.State.PROVISIONING,
             task.State.PENDING,
             task.State.ACTIVATING],
            [
                task.State.FAILED,
                task.State.DEACTIVATING, task.State.STOPPING, task.State.DEPROVISIONING, task.State.STOPPED
            ],
            timeout=120,
        )

        logger.info("Task is running")

        self.environment_api.aws_api.ecs_client.wait_for_status(
            task,
            self.environment_api.aws_api.ecs_client.update_task_information,
            [task.State.DEACTIVATING, task.State.STOPPING, task.State.DEPROVISIONING, task.State.STOPPED],
            [task.State.RUNNING],
            [
                task.State.FAILED,
            ],
            timeout=60*60,
        )
        return True
