"""
Standard ECS maintainer.

"""
import json
from pathlib import Path

from horey.aws_api.aws_services_entities.s3_bucket import S3Bucket
from horey.h_logger import get_logger

from horey.aws_api.aws_services_entities.aws_lambda import AWSLambda
from horey.aws_api.aws_services_entities.event_bridge_rule import EventBridgeRule
from horey.aws_api.aws_services_entities.event_bridge_target import EventBridgeTarget
from horey.aws_api.aws_services_entities.sns_topic import SNSTopic
from horey.aws_api.aws_services_entities.sns_subscription import SNSSubscription
from horey.aws_api.aws_services_entities.lambda_event_source_mapping import LambdaEventSourceMapping
from horey.infrastructure_api.ecs_api import ECSAPI, ECSAPIConfigurationPolicy
from horey.infrastructure_api.build_api import BuildAPI, BuildAPIConfigurationPolicy
from horey.infrastructure_api.aws_iam_api_configuration_policy import AWSIAMAPIConfigurationPolicy
from horey.infrastructure_api.aws_iam_api import AWSIAMAPI
from horey.infrastructure_api.cloudwatch_api_configuration_policy import CloudwatchAPIConfigurationPolicy
from horey.infrastructure_api.cloudwatch_api import CloudwatchAPI
from horey.infrastructure_api.aws_lambda_api_configuration_policy import AWSLambdaAPIConfigurationPolicy
from horey.pip_api.pip_api import PipAPI

logger = get_logger()


class AWSLambdaAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration: AWSLambdaAPIConfigurationPolicy, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api
        self._cloudwatch_api = None
        self._ecs_api = None
        self._aws_iam_api = None
        self._environment_variables_callback = None
        self._alerts_api = None
        self.loadbalancer_api = None
        self._build_api = None

    def init_lambda_name_slug(self):
        """
        Remove all env data.

        :return:
        """

        self.configuration.lambda_name_slug = self.configuration.lambda_name.replace("_", "-")

        for to_clean in ["lambda", self.environment_api.configuration.environment_name,
                         self.environment_api.configuration.environment_level]:
            self.configuration.lambda_name_slug = self.configuration.lambda_name_slug.replace(f"-{to_clean}",
                                                                                              "").replace(
                f"{to_clean}-", "")

        return self.configuration.lambda_name_slug

    @property
    def cloudwatch_api(self):
        """
        Standard.

        :return:
        """
        if self._cloudwatch_api is None:
            config = CloudwatchAPIConfigurationPolicy()
            cloudwatch_api = CloudwatchAPI(configuration=config, environment_api=self.environment_api)
            self.set_api(cloudwatch_api=cloudwatch_api)
        return self._cloudwatch_api

    def environment_variables_callback(self):
        """
        Standard

        :return:
        """

        return {}

    @property
    def aws_iam_api(self):
        """
        Standard

        :return:
        """

        if self._aws_iam_api is None:
            config = AWSIAMAPIConfigurationPolicy()
            self._aws_iam_api = AWSIAMAPI(configuration=config, environment_api=self.environment_api)
            self.init_default_aws_iam_api()
        return self._aws_iam_api

    @aws_iam_api.setter
    def aws_iam_api(self, value):
        """
        Standard

        :return:
        """

        self._aws_iam_api = value

    def init_default_aws_iam_api(self):
        """
        init default values

        :return:
        """

        try:
            self.aws_iam_api.configuration.role_name
        except self.aws_iam_api.configuration.UndefinedValueError:
            try:
                lambda_role_name = self.configuration.lambda_role_name
            except self.aws_iam_api.configuration.UndefinedValueError:
                lambda_role_name = f"role_{self.environment_api.configuration.environment_level}-{self.configuration.lambda_name}"
            self.aws_iam_api.configuration.role_name = lambda_role_name

        try:
            self.aws_iam_api.configuration.assume_role_policy_document
        except self.aws_iam_api.configuration.UndefinedValueError:
            self.aws_iam_api.configuration.assume_role_policy_document = json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "lambda.amazonaws.com"
                            },
                            "Action": "sts:AssumeRole"
                        }
                    ]
                })

    @property
    def ecs_api(self):
        """
        Standard

        :return:
        """

        if self._ecs_api is None:
            config = ECSAPIConfigurationPolicy()
            config.ecr_repository_name_slug = self.init_lambda_name_slug()
            ecs_api = ECSAPI(configuration=config, environment_api=self.environment_api)
            self._ecs_api = ecs_api
        return self._ecs_api

    @ecs_api.setter
    def ecs_api(self, value):
        self._ecs_api = value

    @property
    def build_api(self):
        """
        Standard

        :return:
        """

        if self._build_api is None:
            config = BuildAPIConfigurationPolicy()
            config.docker_repository_uri = self.ecs_api.ecr_repo_uri
            build_api = BuildAPI(configuration=config, environment_api=self.environment_api)
            build_api.git_api = build_api.horey_git_api
            self._build_api = build_api
        return self._build_api

    @build_api.setter
    def build_api(self, value):
        self._build_api = value

    def set_api(self, ecs_api=None, cloudwatch_api=None, loadbalancer_api=None):
        """
        Set api to manage ecs tasks.

        :param cloudwatch_api:
        :param ecs_api:
        :return:
        """

        if cloudwatch_api:
            self._cloudwatch_api = cloudwatch_api

        if ecs_api:
            self.ecs_api = ecs_api
            raise NotImplementedError("""
                        try:
                if self.ecs_api.configuration.ecr_repository_region != self.environment_api.configuration.region:
                    raise RuntimeError(
                        f"{self.ecs_api.configuration.ecr_repository_region} != {self.environment_api.configuration.region=}")
            except self.ecs_api.configuration.UndefinedValueError:
                self.ecs_api.configuration.ecr_repository_region = self.environment_api.configuration.region

            if self.ecs_api.configuration.ecr_repository_policy_text:
                raise NotImplementedError(
                    f"Update policy document: {self.ecs_api.configuration.ecr_repository_policy_text}")

            self.ecs_api.set_api(cloudwatch_api=self.cloudwatch_api)


            """)

        if loadbalancer_api:
            self.loadbalancer_api = loadbalancer_api
            self.loadbalancer_api.configuration.target_type = "lambda"

    @property
    def log_group_name(self):
        """
        Lambda log_group_name

        :return:
        """
        return f"/aws/lambda/{self.configuration.lambda_name}"

    def provision_ecr_repository(self):
        """
        Generate policies and provision.

        :return:
        """
        dict_policy = {"Version": "2008-10-17",
                       "Statement": [
                           {"Sid": "LambdaECRImageRetrievalPolicy",
                            "Effect": "Allow",
                            "Principal": {"Service": "lambda.amazonaws.com"},
                            "Action": ["ecr:BatchGetImage",
                                       "ecr:GetDownloadUrlForLayer",
                                       "ecr:GetRepositoryPolicy"],
                            "Condition": {"StringLike": {
                                "aws:sourceArn":
                                    f"arn:aws:lambda:{self.environment_api.configuration.region}:{self.environment_api.aws_api.ecs_client.account_id}:function:{self.configuration.lambda_name}"}}
                            },
                           {
                               "Sid": "Deployer",
                               "Effect": "Allow",
                               "Principal": "*",
                               "Action": [
                                   "ecr:CompleteLayerUpload",
                                   "ecr:GetAuthorizationToken",
                                   "ecr:UploadLayerPart",
                                   "ecr:InitiateLayerUpload",
                                   "ecr:BatchCheckLayerAvailability",
                                   "ecr:PutImage",
                                   "ecr:BatchGetImage",
                                   "ecr:GetDownloadUrlForLayer",
                                   "ecr:GetRepositoryPolicy"
                               ]
                           }
                       ]}
        self.ecs_api.provision_ecr_repository(repository_policy=json.dumps(dict_policy))

    def provision_docker_lambda(self, branch_name=None, alerts_api=None, from_docker_repository=False) -> AWSLambda:
        """
        Provision ECS infrastructure.

        :return:
        """

        self.configuration.policy["Statement"] += self.lambda_resource_policies_callback()
        self.cloudwatch_api.provision_log_group(self.log_group_name)
        self.provision_ecr_repository()
        self.provision_lambda_role()

        events_rule = self.provision_event_bridge_rule()

        if events_rule:
            statement = {"Sid": f"trigger_{self.configuration.event_bridge_rule_name}",
                         "Effect": "Allow",
                         "Principal": {"Service": "events.amazonaws.com"},
                         "Action": "lambda:InvokeFunction",
                         "Resource": None,
                         "Condition": {"ArnLike": {
                             "AWS:SourceArn": events_rule.arn}}}

            self.configuration.policy["Statement"].append(statement)

        sns_topic = self.provision_sns_topic()
        if sns_topic:
            statement = {
                "Sid": f"trigger_from_topic_{sns_topic.name}",
                "Effect": "Allow",
                "Principal": {"Service": "sns.amazonaws.com"},
                "Action": "lambda:InvokeFunction",
                "Resource": None,
                "Condition": {"ArnLike": {"AWS:SourceArn": sns_topic.arn}},
            }
            self.configuration.policy["Statement"].append(statement)

        aws_lambda = self.update_docker_lambda(branch_name=branch_name, from_docker_repository=from_docker_repository)

        aws_lambda.policy = self.configuration.policy
        self.environment_api.aws_api.lambda_client.provision_lambda_permissions(aws_lambda)

        if events_rule is not None:
            self.provision_event_bridge_rule_targets(events_rule, aws_lambda)

        if sns_topic:
            self.provision_sns_subscription(sns_topic, aws_lambda)

        if self.configuration.event_source_mapping_dynamodb_name:
            self.provision_event_source_mapping_dynamodb(aws_lambda)

        if self.loadbalancer_api:
            raise NotImplementedError("""
                        self.loadbalancer_api.configuration.target_group_targets = [{"Id": aws_lambda.arn}]
            self.loadbalancer_api.provision()
            statement = self.generate_target_group_statement()
            dict_policy = json.loads(aws_lambda.policy)
            statement_ids = [statement["Sid"] for statement in dict_policy["Statement"]]
            if statement["Sid"] not in statement_ids:
                dict_policy["Statement"].append(statement)
                aws_lambda.policy = dict_policy
                if "tmp" not in statement_ids:
                    raise RuntimeError("tmp policy expected to be in the lambda policy")
                self.environment_api.aws_api.lambda_client.provision_lambda_permissions(None, aws_lambda)

            """)

        self.provision_monitoring(alerts_api)
        return aws_lambda

    def lambda_resource_policies_callback(self):
        """
        Standard.

        :return:
        """

        return []

    def provision_lambda_role(self):
        """
        Provision role.

        :return:
        """

        if self.configuration.security_groups:
            managed_policies_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"]
        else:
            managed_policies_arns = []
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }

        inline_policies = self.role_inline_policies_callback() + [self.generate_inline_cloudwatch_policy()]

        self.aws_iam_api.provision_role(assume_role_policy=json.dumps(assume_role_policy),
                                        managed_policies_arns=managed_policies_arns, policies=inline_policies)

    def provision_monitoring(self, alerts_api):
        """
        Provision alert system and alerts.

        :return:
        """

        if alerts_api is None:
            return False

        alerts_api.provision_cloudwatch_logs_alarm(self.log_group_name,
                                                   '"[ERROR]"',
                                                   "error",
                                                   None
                                                   )
        alerts_api.provision_cloudwatch_logs_alarm(self.log_group_name,
                                                   '"Runtime exited with error"',
                                                   "runtime_exited",
                                                   None
                                                   )
        alerts_api.provision_cloudwatch_logs_alarm(self.log_group_name,
                                                   f'"{alerts_api.alert_system.configuration.ALERT_SYSTEM_SELF_MONITORING_LOG_TIMEOUT_FILTER_PATTERN}"',
                                                   "timeout",
                                                   None
                                                   )
        return True

    def provision_event_source_mapping_dynamodb(self, aws_lambda):
        """
        Provision event source mapping for dynamodb stream

        :return:
        """

        table = self.environment_api.get_dynamodb(self.configuration.event_source_mapping_dynamodb_name)
        event_source_mapping = LambdaEventSourceMapping({})
        event_source_mapping.function_arn = aws_lambda.arn
        event_source_mapping.batch_size = 1
        event_source_mapping.region = self.environment_api.region
        event_source_mapping.starting_position = "LATEST"
        event_source_mapping.event_source_arn = table.latest_stream_arn

        event_source_mapping.enabled = True
        event_source_mapping.tags = {tag["Key"]: tag["Value"] for tag in self.environment_api.configuration.tags}
        self.environment_api.aws_api.lambda_client.provision_event_source_mapping(event_source_mapping)

    def provision_sns_topic(self):
        """
        Provision sns topic.

        :return:
        """

        if not self.configuration.provision_sns_topic:
            return None

        topic = SNSTopic({})
        topic.region = self.environment_api.region
        topic.name = self.configuration.sns_topic_name
        topic.attributes = {"DisplayName": topic.name}
        topic.tags = self.environment_api.configuration.tags
        topic.tags.append({"Key": "Name", "Value": topic.name})

        self.environment_api.aws_api.sns_client.provision_topic(topic)
        return topic

    def provision_sns_subscription(self, sns_topic, aws_lambda):
        """
        Subscribe the receiving lambda to the SNS topic.

        @return:
        """

        subscription = SNSSubscription({})
        subscription.region = self.environment_api.region
        subscription.name = f"{aws_lambda.name}_{aws_lambda.region.region_mark}"
        subscription.protocol = "lambda"
        subscription.topic_arn = sns_topic.arn
        subscription.endpoint = aws_lambda.arn
        self.environment_api.aws_api.provision_sns_subscription(subscription)
        return subscription

    def update_docker_lambda(self, branch_name=None, from_docker_repository=False):
        """
        Update lambda code.

        :param branch_name:
        :param from_docker_repository:
        :return:
        """

        if from_docker_repository:
            image_tag_raw = self.ecs_api.fetch_latest_artifact_metadata().image_tags[0]
            image_registry_reference = self.ecs_api.generate_image_registry_reference(image_tag_raw)
        else:
            build_number = self.ecs_api.get_next_build_number()

            image = self.build_api.run_build_image_routine(branch_name, build_number)

            image_registry_reference = image.tags[0]

        return self.deploy_lambda(image_registry_reference)

    def get_latest_build_number(self):
        """
        Latest build number from ecr repo

        :return:
        """

        for image in self.ecs_api.ecr_images:
            build_numbers = [int(build_subtag.split("_")[1]) for str_image_tag in image.image_tags for build_subtag in
                             str_image_tag.split("-") if build_subtag.startswith("build_")]
            image.build_number = max(build_numbers)

        try:
            return max(self.ecs_api.ecr_images, key=lambda _image: _image.build_number)
        except ValueError as inst_error:
            if "iterable argument is empty" not in repr(inst_error) and "arg is an empty sequence" not in repr(
                    inst_error):
                raise

        return None

    def deploy_lambda(self, image_registry_reference):
        """
        Deploy the code.

        :return:
        """

        aws_lambda = AWSLambda({})
        aws_lambda.region = self.environment_api.region
        aws_lambda.name = self.configuration.lambda_name

        iam_role = self.aws_iam_api.get_role()
        aws_lambda.role = iam_role.arn

        aws_lambda.tags = {tag["Key"]: tag["Value"] for tag in self.environment_api.configuration.tags}
        aws_lambda.tags["Name"] = aws_lambda.name

        if self.configuration.security_groups:
            security_groups = self.environment_api.get_security_groups(self.configuration.security_groups)
            aws_lambda.vpc_config = {
                "SubnetIds": [subnet.id for subnet in self.environment_api.private_subnets],
                "SecurityGroupIds": [
                    security_group.id for security_group in security_groups
                ]
            }
        aws_lambda.timeout = self.configuration.lambda_timeout
        aws_lambda.memory_size = self.configuration.lambda_memory_size
        if self.configuration.reserved_concurrent_executions:
            aws_lambda.reserved_concurrent_executions = self.configuration.reserved_concurrent_executions

        aws_lambda.environment = self.environment_variables_callback()

        if self.loadbalancer_api:
            try:
                statement = self.generate_target_group_statement()
                aws_lambda.policy["Statement"].append(statement)
            except RuntimeError as inst_error:
                statement = {
                    "Sid": "tmp",
                    "Effect": "Allow",
                    "Principal": {"Service": "elasticloadbalancing.amazonaws.com"},
                    "Action": "lambda:InvokeFunction",
                    "Resource": None
                }
                aws_lambda.policy["Statement"].append(statement)
                if "Was not able to find target group" not in repr(inst_error):
                    raise

        aws_lambda.code = {"ImageUri": image_registry_reference}
        self.environment_api.aws_api.provision_aws_lambda(aws_lambda, update_code=True)
        return aws_lambda

    def generate_target_group_statement(self):
        """
        Permissions statement.

        :param self:
        :return:
        """

        target_group = self.loadbalancer_api.get_targetgroup()
        return {
            "Sid": f"trigger_from_{self.loadbalancer_api.configuration.target_group_name}",
            "Effect": "Allow",
            "Principal": {"Service": "elasticloadbalancing.amazonaws.com"},
            "Action": "lambda:InvokeFunction",
            "Resource": None,
            "Condition": {"ArnLike": {"AWS:SourceArn": target_group.arn}},
        }

    def provision_event_bridge_rule(self):
        """
        Event bridge rule - the trigger used to trigger the lambda each minute.

        :return:
        """

        if not self.configuration.schedule_expression:
            return None

        rule = EventBridgeRule({})
        rule.name = self.configuration.event_bridge_rule_name
        rule.description = f"{self.configuration.lambda_name} triggering rule"
        rule.region = self.environment_api.region
        rule.schedule_expression = self.configuration.schedule_expression
        rule.event_bus_name = "default"
        rule.state = "ENABLED"
        # rule.state = "DISABLED"
        rule.tags = self.environment_api.get_tags_with_name(rule.name)

        self.environment_api.aws_api.provision_events_rule(rule)
        return rule

    def provision_event_bridge_rule_targets(self, events_rule, aws_lambda):
        """
        Event rule - triggering salesforce.

        :param events_rule:
        :param aws_lambda:
        :return:
        """

        target = EventBridgeTarget({})
        target.id = f"target-{self.configuration.lambda_name}"
        target.arn = aws_lambda.arn

        events_rule.targets = [target]
        self.environment_api.aws_api.provision_events_rule(events_rule)

    def get_lambda(self):
        """
        Get lambda object.

        :return:
        """

        aws_lambda = AWSLambda({})
        aws_lambda.region = self.environment_api.region
        aws_lambda.name = self.configuration.lambda_name
        if not self.environment_api.aws_api.lambda_client.update_lambda_information(aws_lambda):
            raise RuntimeError(f"Lambda '{aws_lambda.name}' not found in {self.environment_api.configuration.region}")
        return aws_lambda

    def generate_inline_cloudwatch_policy(self):
        """
        Cloudwatch access

        :return:
        """
        statements = [
            {
                "Action": [
                    "cloudwatch:SetAlarmState",
                    "cloudwatch:DescribeAlarms"
                ],
                "Resource": [
                    f"arn:aws:cloudwatch:{self.environment_api.configuration.region}:{self.environment_api.aws_api.lambda_client.account_id}:alarm:*"
                ],
                "Effect": "Allow"
            },
            {
                "Sid": "CloudwatchLogs",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": [
                    "*"
                ]
            }
        ]

        return self.environment_api.generate_inline_policy(name="inline_cloudwatch",
                                                           description="Cloudwatch access policy",
                                                           statements=statements)

    def role_inline_policies_callback(self):
        """
        Made for async generation.

        :return:
        """

        inline_policies = []
        if self.configuration.event_source_mapping_dynamodb_name:
            name = f"inline_event_source_{self.configuration.event_source_mapping_dynamodb_name}"
            table = self.environment_api.get_dynamodb(self.configuration.event_source_mapping_dynamodb_name)

            policy = self.aws_iam_api.generate_inline_policy(name, [
                table.latest_stream_arn
            ], [
                                                                 "dynamodb:GetRecords",
                                                                 "dynamodb:GetShardIterator",
                                                                 "dynamodb:DescribeStream",
                                                                 "dynamodb:ListStreams"
                                                             ])
            inline_policies.append(policy)

        return inline_policies

    def provision_echo_lambda(self) -> AWSLambda:
        """
        Provision lambda to echo the event.

        :return:
        """

        self.configuration.lambda_name = f"echo_{self.environment_api.configuration.region}"
        self.configuration.lambda_timeout = 30
        self.configuration.lambda_memory_size = 1024
        self.init_lambda_name_slug()

        self.build_api.prepare_source_code_directory = self.prepare_echo_lambda_source_code_directory

        return self.provision_docker_lambda()

    def prepare_echo_lambda_source_code_directory(self, branch_name):
        """
        Generate Dockerfile and horey repos.

        :param branch_name:
        :return:
        """

        if branch_name is not None:
            raise RuntimeError("Not implemented")

        path = self.build_api.init_temporary_source_code_directory()

        self.build_api.git_api.update_local_source_code("main")

        PipAPI.copy_horey_package_required_packages("h_logger", path,
                                                    self.build_api.git_api.configuration.directory_path)

        self.generate_lambda_dockerfile(path)
        self.generate_echo_lambda_code(path)
        return path

    @staticmethod
    def generate_lambda_dockerfile(dir_path: Path):
        """
        Generate Dockerfile.

        :return:
        """

        dockerfile_path = dir_path / "Dockerfile"
        with open(dockerfile_path, "w", encoding="utf-8") as file_handler:
            file_handler.write(
                "FROM public.ecr.aws/lambda/python:3.12\n"
                "ARG HOREY_FOLDER_NAME=horey\n"
                "COPY ${HOREY_FOLDER_NAME} ${LAMBDA_TASK_ROOT}/horey\n"
                "COPY lambda_handler.py ${LAMBDA_TASK_ROOT}/\n"
                "RUN dnf install -y git make wget which findutils\n"
                "RUN wget https://bootstrap.pypa.io/get-pip.py\n"
                "RUN python get-pip.py\n"
                "RUN rm get-pip.py\n"
                "RUN python ${LAMBDA_TASK_ROOT}/horey/pip_api/horey/pip_api/pip_api_make.py --install horey.h_logger --pip_api_configuration ${LAMBDA_TASK_ROOT}/horey/pip_api_docker_configuration.py\n"
                "CMD [ \"lambda_handler.handler\" ]\n"
            )
        return dockerfile_path

    @staticmethod
    def generate_echo_lambda_code(dir_path: Path):
        """
        Generate lambda handler code.

        :return:
        """

        lambda_handler_path = dir_path / "lambda_handler.py"
        with open(lambda_handler_path, "w", encoding="utf-8") as file_handler:
            file_handler.write(
                "from horey.h_logger import get_logger\n\n"
                "logger = get_logger()\n\n\n"
                "def handler(event, context):\n"
                "    logger.info(f\"Event: {event}\")\n"
                "    logger.info(f\"Context: {context}\")\n"
                "    return {\n"
                "        'statusCode': 200,\n"
                "        'body': 'Event logged successfully'\n"
                "    }\n"
            )
        return lambda_handler_path

    @staticmethod
    def generate_s3_trigger_statement(bucket:S3Bucket):
        """
        Generate statement

        :param bucket:
        :return:
        """

        sid = f"trigger_s3_{bucket.name}"
        sid = sid.replace(".", "_")
        return {"Sid": sid,
                     "Effect": "Allow",
                     "Principal": {"Service": "s3.amazonaws.com"},
                     "Action": "lambda:InvokeFunction",
                     "Resource": None,
                     "Condition": {"ArnLike": {
                         "AWS:SourceArn": bucket.arn}}}
