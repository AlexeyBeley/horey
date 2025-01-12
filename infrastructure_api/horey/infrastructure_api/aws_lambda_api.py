"""
Standard ECS maintainer.

"""
import json

from horey.h_logger import get_logger

from horey.aws_api.aws_services_entities.aws_lambda import AWSLambda
from horey.aws_api.aws_services_entities.event_bridge_rule import EventBridgeRule
from horey.aws_api.aws_services_entities.event_bridge_target import EventBridgeTarget
from horey.aws_api.aws_services_entities.sns_topic import SNSTopic
from horey.aws_api.aws_services_entities.sns_subscription import SNSSubscription
from horey.aws_api.aws_services_entities.lambda_event_source_mapping import LambdaEventSourceMapping
from horey.infrastructure_api.ecs_api_configuration_policy import ECSAPIConfigurationPolicy
from horey.infrastructure_api.ecs_api import ECSAPI
from horey.infrastructure_api.aws_iam_api_configuration_policy import AWSIAMAPIConfigurationPolicy
from horey.infrastructure_api.aws_iam_api import AWSIAMAPI
from horey.infrastructure_api.cloudwatch_api_configuration_policy import CloudwatchAPIConfigurationPolicy
from horey.infrastructure_api.cloudwatch_api import CloudwatchAPI

logger = get_logger()


class AWSLambdaAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api
        self.cloudwatch_api = None
        self._ecs_api = None
        self._aws_iam_api = None
        self._environment_variables_callback = None

    @property
    def environment_variables_callback(self):
        """
        Standard

        :return:
        """

        if self._environment_variables_callback is None:
            self._environment_variables_callback = lambda: self.configuration.environment_variables
        return self._environment_variables_callback

    @environment_variables_callback.setter
    def environment_variables_callback(self, value):
        self._environment_variables_callback = value

    @property
    def aws_iam_api(self):
        """
        Standard

        :return:
        """

        if self._aws_iam_api is None:
            config = AWSIAMAPIConfigurationPolicy()
            aws_iam_api = AWSIAMAPI(configuration=config, environment_api=self.environment_api)
            self.set_apis(aws_iam_api=aws_iam_api)
        return self._aws_iam_api

    @aws_iam_api.setter
    def aws_iam_api(self, value):
        """
        Standard

        :return:
        """

        self._aws_iam_api = value

    @property
    def ecs_api(self):
        """
        Standard

        :return:
        """

        if self._ecs_api is None:
            config = ECSAPIConfigurationPolicy()
            ecs_api = ECSAPI(configuration=config, environment_api=self.environment_api)
            self.set_apis(ecs_api=ecs_api)
        return self._ecs_api

    @ecs_api.setter
    def ecs_api(self, value):
        self._ecs_api = value

    def set_apis(self, ecs_api=None, cloudwatch_api=None, aws_iam_api=None):
        """
        Set api to manage ecs tasks.

        :param aws_iam_api:
        :param cloudwatch_api:
        :param ecs_api:
        :return:
        """

        if cloudwatch_api:
            self.cloudwatch_api = cloudwatch_api
            try:
                self.cloudwatch_api.configuration.log_group_name
            except self.cloudwatch_api.configuration.UndefinedValueError:
                self.cloudwatch_api.configuration.log_group_name = f"/aws/lambda/{self.configuration.lambda_name}"

        if ecs_api:
            self.ecs_api = ecs_api
            try:
                self.ecs_api.configuration.ecr_repository_name
            except self.ecs_api.configuration.UndefinedValueError:
                self.ecs_api.configuration.ecr_repository_name = f"repo_{self.configuration.lambda_name}"

            try:
                self.ecs_api.configuration.ecr_repository_region
            except self.ecs_api.configuration.UndefinedValueError:
                self.ecs_api.configuration.ecr_repository_region = self.configuration.ecr_repository_region

            try:
                raise RuntimeError(self.ecs_api.configuration.ecr_repository_policy_text)
            except self.ecs_api.configuration.UndefinedValueError:
                dict_policy = {"Version": "2008-10-17",
                               "Statement": [
                                   {"Sid": "LambdaECRImageRetrievalPolicy",
                                    "Effect": "Allow",
                                    "Principal": {"Service": "lambda.amazonaws.com"},
                                    "Action": ["ecr:BatchGetImage",
                                               "ecr:GetDownloadUrlForLayer",
                                               "ecr:GetRepositoryPolicy"],
                                    "Condition": {"StringLike": {
                                        "aws:sourceArn": f"arn:aws:lambda:{self.environment_api.configuration.region}:{self.environment_api.aws_api.ecs_client.account_id}:function:{self.configuration.lambda_name}"}}}]}

                self.ecs_api.configuration.ecr_repository_policy_text = json.dumps(dict_policy)

        if aws_iam_api:
            self.aws_iam_api = aws_iam_api
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

    def provision(self, branch_name=None, inline_policies=None):
        """
        Provision ECS infrastructure.

        :return:
        """
        self.environment_api.aws_api.lambda_client.clear_cache(None, all_cache=True)

        if self.cloudwatch_api is None:
            config = CloudwatchAPIConfigurationPolicy()
            cloudwatch_api = CloudwatchAPI(configuration=config, environment_api=self.environment_api)
            self.set_apis(cloudwatch_api=cloudwatch_api)

        self.cloudwatch_api.provision()
        self.ecs_api.provision()
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

        inline_policies = inline_policies or []
        if self.configuration.event_source_mapping_dynamodb_name:
            # todo: generate cleanup report to find lambdas with no permissions
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

        self.aws_iam_api.provision_role(assume_role_policy=json.dumps(assume_role_policy),
                                        managed_policies_arns=managed_policies_arns, policies=inline_policies)

        events_rule = self.provision_events_rule() if self.configuration.schedule_expression is not None else None

        sns_topic = self.provision_sns_topic() if self.configuration.provision_sns_topic else None

        aws_lambda = self.update(branch_name=branch_name, events_rule=events_rule, sns_topic=sns_topic)
        if events_rule is not None:
            self.provision_events_rule_targets(events_rule, aws_lambda)
        if sns_topic:
            self.provision_sns_subscription(sns_topic, aws_lambda)

        if self.configuration.event_source_mapping_dynamodb_name:
            self.provision_event_source_mapping_dynamodb(aws_lambda)

        # todo: self.provision_alert_system([])
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

    def update(self, branch_name=None, events_rule=None, sns_topic=None):
        """

        :return:
        """
        ecr_image = self.get_latest_build()
        build_number = ecr_image.build_number if ecr_image is not None else -1

        repo_uri = f"{self.environment_api.aws_api.ecs_client.account_id}.dkr.ecr.{self.ecs_api.configuration.ecr_repository_region}.amazonaws.com/{self.ecs_api.configuration.ecr_repository_name}"
        if branch_name is not None:
            if not self.environment_api.git_api.checkout_remote_branch(self.configuration.git_remote_url, branch_name):
                raise RuntimeError(f"Was not able to checkout branch: {branch_name}")

            commit_id = self.environment_api.git_api.get_commit_id()

            tags = [f"{repo_uri}:build_{build_number + 1}-commit_{commit_id}"]
            image = self.environment_api.build_and_upload_ecr_image(
                self.environment_api.git_api.configuration.directory_path, tags, False)
            image_tag = image.tags[-1]
        elif ecr_image is None:
            raise RuntimeError(f"Images store '{repo_uri}' is empty yet, use branch_name to build and image")
        else:
            image_tag_raw = ecr_image.image_tags[-1]
            image_tag = f"{repo_uri}:{image_tag_raw}"
        return self.deploy_lambda(image_tag, events_rule=events_rule, sns_topic=sns_topic)

    def get_latest_build(self):
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

    def deploy_lambda(self, image_tag, events_rule=None, sns_topic=None):
        """
        Deploy the code.

        :return:
        """
        iam_role = self.aws_iam_api.get_role()

        if self.configuration.schedule_expression and events_rule is None:
            events_rule = EventBridgeRule({})
            events_rule.name = self.configuration.event_bridge_rule_name
            events_rule.region = self.environment_api.region
            if not self.environment_api.aws_api.events_client.update_rule_information(events_rule):
                raise RuntimeError(f"Was not able to find event rule {self.configuration.event_bridge_rule_name}")

        if self.configuration.provision_sns_topic and sns_topic is None:
            sns_topic = self.environment_api.get_sns_topic(self.configuration.sns_topic_name)

        security_groups = self.environment_api.get_security_groups(self.configuration.security_groups)

        aws_lambda = AWSLambda({})
        aws_lambda.region = self.environment_api.region
        aws_lambda.name = self.configuration.lambda_name
        aws_lambda.role = iam_role.arn

        aws_lambda.tags = {tag["Key"]: tag["Value"] for tag in self.environment_api.configuration.tags}
        aws_lambda.tags["Name"] = aws_lambda.name

        aws_lambda.vpc_config = {
            "SubnetIds": [subnet.id for subnet in self.environment_api.private_subnets],
            "SecurityGroupIds": [
                security_group.id for security_group in security_groups
            ]
        }
        aws_lambda.timeout = 600
        aws_lambda.memory_size = 192
        aws_lambda.reserved_concurrent_executions = 1

        aws_lambda.environment = self.environment_variables_callback()

        if self.configuration.schedule_expression:
            aws_lambda.policy = {"Version": "2012-10-17",
                                 "Id": "default",
                                 "Statement": [
                                     {"Sid": f"trigger_{self.configuration.event_bridge_rule_name}",
                                      "Effect": "Allow",
                                      "Principal": {"Service": "events.amazonaws.com"},
                                      "Action": "lambda:InvokeFunction",
                                      "Resource": None,
                                      "Condition": {"ArnLike": {
                                          "AWS:SourceArn": events_rule.arn}}}]}
        if sns_topic:
            if not aws_lambda.policy:
                aws_lambda.policy = {"Version": "2012-10-17",
                                     "Id": "default",
                                     "Statement": []}
            statement = {
                "Sid": f"trigger_from_topic_{sns_topic.name}",
                "Effect": "Allow",
                "Principal": {"Service": "sns.amazonaws.com"},
                "Action": "lambda:InvokeFunction",
                "Resource": None,
                "Condition": {"ArnLike": {"AWS:SourceArn": sns_topic.arn}},
            }
            aws_lambda.policy["Statement"].append(statement)

        aws_lambda.code = {"ImageUri": image_tag}
        self.environment_api.aws_api.provision_aws_lambda(aws_lambda, force=True)
        return aws_lambda

    def provision_events_rule(self):
        """
        Event bridge rule - the trigger used to trigger the lambda each minute.

        :return:
        """

        rule = EventBridgeRule({})
        rule.name = self.configuration.event_bridge_rule_name
        rule.description = f"{self.configuration.lambda_name} triggering rule"
        rule.region = self.environment_api.region
        rule.schedule_expression = self.configuration.schedule_expression
        rule.event_bus_name = "default"
        rule.state = "ENABLED"
        rule.tags = self.environment_api.configuration.tags
        rule.tags.append({
            "Key": "Name",
            "Value": rule.name
        })

        self.environment_api.aws_api.provision_events_rule(rule)
        return rule

    def provision_events_rule_targets(self, events_rule, aws_lambda):
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

    def get_lamda(self):
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
