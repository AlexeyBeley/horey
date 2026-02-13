"""
Standard s3 manager

"""

from horey.aws_api.aws_services_entities.aws_lambda import AWSLambda
from horey.aws_api.aws_services_entities.s3_bucket import S3Bucket
from horey.infrastructure_api.environment_api import EnvironmentAPI
from horey.infrastructure_api.s3_api_configuration_policy import S3APIConfigurationPolicy


class S3API:
    """
    Manage Frontend.

    """

    def __init__(self, configuration: S3APIConfigurationPolicy, environment_api: EnvironmentAPI):
        self.configuration = configuration
        self.environment_api = environment_api

    def provision_bucket(self, bucket: S3Bucket):
        """
        Provision the bucket.

        :return:
        """

        if bucket.region is None:
            bucket.region = self.environment_api.region
        return self.environment_api.aws_api.provision_s3_bucket(bucket)

    def get_bucket(self, bucket_name: str):
        """
        Find the bucket by name

        :return:
        """

        bucket = S3Bucket({"Name": bucket_name})

        if self.environment_api.aws_api.s3_client.update_bucket_information(bucket):
            return bucket

        return None

    def add_bucket_notification_configuration_lambda(self, bucket: S3Bucket, aws_lambda: AWSLambda,
                                                      bucket_objects_filter=None):
        """
        Provision the bucket.

        Error: Configuration is ambiguously defined. Cannot have overlapping suffixes
        in two rules if the prefixes are overlapping for the same event type.

        :return:
        """

        dict_configuration = self.environment_api.aws_api.s3_client.get_bucket_notification_configuration(bucket)
        del dict_configuration["ResponseMetadata"]

        lambdas_configs = dict_configuration.get("LambdaFunctionConfigurations", [])
        if aws_lambda.arn in [_lambda_config["LambdaFunctionArn"] for _lambda_config in lambdas_configs]:
            return True

        dict_new_lambda = {
            "LambdaFunctionArn": aws_lambda.arn,
            "Events": ["s3:ObjectCreated:*", "s3:ObjectRemoved:*"]
        }

        if bucket_objects_filter is not None:
            dict_new_lambda["Filter"] = {"Key": {"FilterRules": [{"Name": "Prefix", "Value": bucket_objects_filter}]}}
        lambdas_configs.append(dict_new_lambda)

        dict_configuration["LambdaFunctionConfigurations"] = lambdas_configs

        return self.environment_api.aws_api.s3_client.provision_bucket_notification_configuration(bucket, dict_configuration)

    def provision_bucket_notification_configuration_lambda(self, bucket: S3Bucket, aws_lambda: AWSLambda,
                                                     bucket_objects_filter=None):
        """
        Provision the bucket.

        Error: Configuration is ambiguously defined. Cannot have overlapping suffixes
        in two rules if the prefixes are overlapping for the same event type.

        https://docs.aws.amazon.com/AmazonS3/latest/userguide/notification-how-to-event-types-and-destinations.html#supported-notification-event-types

        :return:
        """

        dict_configuration = self.environment_api.aws_api.s3_client.get_bucket_notification_configuration(bucket)
        del dict_configuration["ResponseMetadata"]

        lambdas_configs = dict_configuration.get("LambdaFunctionConfigurations", [])
        if aws_lambda.arn in [_lambda_config["LambdaFunctionArn"] for _lambda_config in lambdas_configs]:
            return True

        dict_new_lambda = {
            "LambdaFunctionArn": aws_lambda.arn,
            "Events": ["s3:ObjectCreated:*", "s3:ObjectRemoved:*"]
        }

        if bucket_objects_filter is not None:
            dict_new_lambda["Filter"] = {"Key": {"FilterRules": [{"Name": "Prefix", "Value": bucket_objects_filter}]}}
        lambdas_configs = [dict_new_lambda]

        dict_configuration["LambdaFunctionConfigurations"] = lambdas_configs

        return self.environment_api.aws_api.s3_client.provision_bucket_notification_configuration(bucket,
                                                                                                  dict_configuration)
