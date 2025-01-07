"""
Standard ECS maintainer.

"""
import json

from horey.h_logger import get_logger

from horey.aws_api.aws_services_entities.aws_lambda import AWSLambda
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
        if self._environment_variables_callback is None:
            self._environment_variables_callback = lambda: self.configuration.environment_variables
        return self._environment_variables_callback

    @environment_variables_callback.setter
    def environment_variables_callback(self, value):
        self._environment_variables_callback = value

    @property
    def aws_iam_api(self):
        if self._aws_iam_api is None:
            config = AWSIAMAPIConfigurationPolicy()
            aws_iam_api = AWSIAMAPI(configuration=config, environment_api=self.environment_api)
            self.set_apis(aws_iam_api=aws_iam_api)
        return self._aws_iam_api

    @aws_iam_api.setter
    def aws_iam_api(self, value):
        self._aws_iam_api = value

    @property
    def ecs_api(self):
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

    def provision(self, branch_name=None):
        """
        Provision ECS infrastructure.

        :return:
        """

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
        self.aws_iam_api.provision_role(assume_role_policy=json.dumps(assume_role_policy), managed_policies_arns=managed_policies_arns)

        # todo: self.provision_events_rule()
        # todo: self.provision_alert_system([])
        self.update(branch_name=branch_name)

    def update(self, branch_name=None):
        """

        :return:
        """

        build_number = self.get_latest_build_number()
        if not self.environment_api.git_api.checkout_remote_branch(self.configuration.git_remote_url, branch_name):
            raise RuntimeError(f"Was not able to checkout branch: {branch_name}")
        commit_id = self.environment_api.git_api.get_commit_id()

        repo_uri = f"{self.environment_api.aws_api.ecs_client.account_id}.dkr.ecr.{self.ecs_api.configuration.ecr_repository_region}.amazonaws.com/{self.ecs_api.configuration.ecr_repository_name}"

        tags = [f"{repo_uri}:build_{build_number + 1}-commit_{commit_id}"]
        image = self.environment_api.build_and_upload_ecr_image(self.environment_api.git_api.configuration.directory_path, tags, False)
        self.deploy_lambda(image)
        return True

    def get_latest_build_number(self):
        """
        Latest build number from ecr repo

        :return: 
        """

        build_numer = -1
        for image in self.ecs_api.ecr_images:
            build_numbers = [int(build_subtag.split("_")[1]) for str_image_tag in image.image_tags for build_subtag in str_image_tag.split("-") if build_subtag.startswith("build_")]
            build_numer = max(max(build_numbers), build_numer)
        return build_numer

    def deploy_lambda(self, image):
        """
        Deploy the code.

        :return:
        """
        iam_role = self.aws_iam_api.get_role()

        #events_rule = EventBridgeRule({})
        #events_rule.name = self.configuration.event_bridge_rule_name
        #events_rule.region = self.region
        #self.aws_api.events_client.update_rule_information(events_rule)

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

        #aws_lambda.policy = {"Version": "2012-10-17",
        #                     "Id": "default",
        #                     "Statement": [
        #                         {"Sid": f"trigger_{self.configuration.event_bridge_rule_name}",
        #                          "Effect": "Allow",
        #                          "Principal": {"Service": "events.amazonaws.com"},
        #                          "Action": "lambda:InvokeFunction",
        #                          "Resource": None,
        #                          "Condition": {"ArnLike": {
        #                              "AWS:SourceArn": events_rule.arn}}}]}

        aws_lambda.code = {"ImageUri": image.tags[-1]}
        self.environment_api.aws_api.provision_aws_lambda(aws_lambda, force=True)
        return aws_lambda
