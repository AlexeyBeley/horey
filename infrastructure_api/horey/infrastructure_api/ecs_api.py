"""
Standard ECS maintainer.

"""
import copy
import json
import os
from datetime import datetime

from horey.h_logger import get_logger

from horey.aws_api.aws_services_entities.ecr_image import ECRImage
from horey.aws_api.aws_services_entities.ecr_repository import ECRRepository
from horey.aws_api.base_entities.region import Region
from horey.infrastructure_api.alerts_api import AlertsAPI
from horey.infrastructure_api.alerts_api_configuration_policy import AlertsAPIConfigurationPolicy
from horey.infrastructure_api.cloudwatch_api_configuration_policy import CloudwatchAPIConfigurationPolicy
from horey.infrastructure_api.aws_iam_api_configuration_policy import AWSIAMAPIConfigurationPolicy
from horey.infrastructure_api.aws_iam_api import AWSIAMAPI
from horey.infrastructure_api.cloudwatch_api import CloudwatchAPI

logger = get_logger()


class ECSAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api
        self._ecr_repository = None
        self._ecr_images = None
        self._alerts_api = None
        self._cloudwatch_api = None
        self._aws_iam_api = None
        self.loadbalancer_api = None
        self.dns_api = None
        self.loadbalancer_dns_api_pairs =None

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

        :param loadbalancer_api:
        :param dns_api:
        :return:
        """
        if loadbalancer_dns_api_pairs:
            if loadbalancer_api or dns_api:
                raise NotImplementedError(f"You can not both declare loadbalancer_dns_apis_pairs and either lb_api or dns_api")
            for loadbalancer_api, dns_api in loadbalancer_dns_api_pairs:
                assert self.loadbalancer_api.configuration.load_balancer_name
                assert self.loadbalancer_api.configuration.target_group_name

            self.loadbalancer_dns_api_pairs = loadbalancer_dns_api_pairs

        if loadbalancer_api:
            self.loadbalancer_api = loadbalancer_api
            try:
                self.loadbalancer_api.configuration.target_group_name
            except self.loadbalancer_api.configuration.UndefinedValueError:
                self.loadbalancer_api.configuration.target_group_name = f"tg-{self.configuration.cluster_name.replace('cluster_', '')}-{self.configuration.service_name}".replace(
                    "_", "-")

            try:
                self.loadbalancer_api.configuration.load_balancer_name
            except self.loadbalancer_api.configuration.UndefinedValueError:
                self.loadbalancer_api.configuration.load_balancer_name = f"lb-{self.configuration.cluster_name.replace('cluster_', '')}".replace(
                    "_", "-")

        if dns_api:
            self.dns_api = dns_api

        if cloudwatch_api:
            if not cloudwatch_api.configuration.log_group_name:
                raise ValueError("Log group name not set")
            self.cloudwatch_api = cloudwatch_api

    def provision(self):
        """
        Provision ECS infrastructure.

        :return:
        """

        self.environment_api.aws_api.lambda_client.clear_cache(None, all_cache=True)
        self.provision_ecr_repository()

        try:
            provision_service = self.configuration.service_name is not None
        except self.configuration.UndefinedValueError as error_inst:
            if "service_name" not in repr(error_inst):
                raise
            provision_service = False

        if provision_service:
            self.cloudwatch_api.provision()
            self.provision_monitoring()
            self.provision_task_role()
            self.provision_execution_role()

        if self.loadbalancer_api:
            self.loadbalancer_api.provision()

        if provision_service:
            self.update()

        if self.dns_api:
            self.dns_api.configuration.dns_target = self.loadbalancer_api.get_loadbalancer().dns_name
            self.dns_api.provision()
        elif self.loadbalancer_dns_api_pairs:
            for loadbalancer_api, dns_api in self.loadbalancer_dns_api_pairs:
                dns_api.configuration.dns_target = loadbalancer_api.get_loadbalancer().dns_name
                dns_api.provision()

        return True

    def environment_variables_callback(self):
        """
        Made for async generation.

        :return:
        """

        return []

    def role_inline_policies_callback(self):
        """
        Made for async generation.

        :return:
        """

        return []

    def prepare_container_build_directory_callback(self, source_code_dir):
        """
        Echo.

        :param source_code_dir:
        :return:
        """

        return source_code_dir

    def update(self):
        """

        :return:
        """

        self.configuration.ecr_image_id = self.get_ecr_image()
        ecs_task_definition = self.provision_ecs_task_definition()

        return self.provision_ecs_service(ecs_task_definition)

    def provision_ecs_task_definition(self):
        """
        Provision task definition.

        :return:
        """

        task_definition = self.environment_api.provision_ecs_fargate_task_definition(
            task_definition_family=self.configuration.family,
            contaner_name=self.configuration.container_name,
            ecr_image_id=self.configuration.ecr_image_id,
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

        security_groups = self.environment_api.get_security_groups(self.configuration.security_groups)
        if self.loadbalancer_api:
            target_groups = [self.loadbalancer_api.get_targetgroup()]
        elif self.loadbalancer_dns_api_pairs:
            target_groups = [loadbalancer_api.get_targetgroup() for loadbalancer_api in self.loadbalancer_dns_api_pairs]
        else:
            target_groups = []

        load_blanacer_dicts = [{
            "targetGroupArn": target_group.arn,
            "containerName": self.configuration.container_name,
            "containerPort": self.configuration.container_definition_port_mappings[0]["containerPort"]
        } for target_group in target_groups
        ]

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
                                                          load_blanacer_dicts=load_blanacer_dicts
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
        repo.tags = copy.deepcopy(self.environment_api.configuration.tags)
        repo.tags.append({
            "Key": "Name",
            "Value": repo.name
        })

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

    def get_ecr_image(self, nocache=False):
        """
        Build if needed.
        Upload if needed.
        Download if needed.

        :param nocache:
        :return:
        """
        ecr_image = self.get_latest_build()
        build_number = ecr_image.build_number if ecr_image is not None else -1
        repo_uri = f"{self.environment_api.aws_api.ecs_client.account_id}.dkr.ecr.{self.configuration.ecr_repository_region}.amazonaws.com/{self.configuration.ecr_repository_name}"
        if self.environment_api.git_api.configuration.branch_name is not None:
            if not self.environment_api.git_api.checkout_remote_branch():
                raise RuntimeError(
                    f"Was not able to checkout branch: {self.environment_api.git_api.configuration.branch_name}")

            commit_id = self.environment_api.git_api.get_commit_id()

            tags = [f"{repo_uri}:build_{build_number + 1}-commit_{commit_id}"]
            image = self.environment_api.build_and_upload_ecr_image(
                self.prepare_container_build_directory_callback(
                    self.environment_api.git_api.configuration.directory_path), tags, nocache,
                buildargs=self.configuration.buildargs)
            assert tags[0] in image.tags
            image_tag = tags[0]
        elif ecr_image is None:
            raise RuntimeError(f"Images store '{repo_uri}' is empty yet, use branch_name to build an image")
        else:
            image_tag_raw = ecr_image.image_tags[-1]
            image_tag = f"{repo_uri}:{image_tag_raw}"

        return image_tag

    def get_latest_build(self):
        """
        Latest build number from ecr repo

        :return:
        """

        for image in self.ecr_images:
            build_numbers = [int(build_subtag.split("_")[1]) for str_image_tag in image.image_tags for build_subtag in
                             str_image_tag.split("-") if build_subtag.startswith("build_")]
            image.build_number = max(build_numbers)

        try:
            return max(self.ecr_images, key=lambda _image: _image.build_number)
        except ValueError as inst_error:
            if "iterable argument is empty" not in repr(inst_error) and "arg is an empty sequence" not in repr(
                    inst_error):
                raise

        return None

    @property
    def alerts_api(self):
        """
        Alerts api

        :return:
        """

        if self._alerts_api is None:
            alerts_api_configuration = AlertsAPIConfigurationPolicy()
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
        self.alerts_api.provision_cloudwatch_logs_alarm(self.cloudwatch_api.configuration.log_group_name, '"[ERROR]"',
                                                        "error", None, dimensions=None,
                                                        alarm_description=None)
        self.alerts_api.provision_cloudwatch_logs_alarm(self.cloudwatch_api.configuration.log_group_name,
                                                        '"Runtime exited with error"', "runtime_exited", None,
                                                        dimensions=None,
                                                        alarm_description=None)
        self.alerts_api.provision_cloudwatch_logs_alarm(self.cloudwatch_api.configuration.log_group_name,
                                                        f'"{self.alerts_api.alert_system.configuration.ALERT_SYSTEM_SELF_MONITORING_LOG_TIMEOUT_FILTER_PATTERN}"',
                                                        "timeout", None, dimensions=None,
                                                        alarm_description=None)
        return True

    def provision_task_role(self):
        """
        Provision role used by the task.

        :return:
        """

        if not self.configuration.service_name:
            return True

        policies = self.role_inline_policies_callback()
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

        if not self.configuration.service_name:
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
