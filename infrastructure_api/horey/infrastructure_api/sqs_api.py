"""
Standard Load balancing maintainer.

"""
import json

from horey.h_logger import get_logger
from horey.aws_api.aws_services_entities.sqs_queue import SQSQueue

from horey.infrastructure_api.sqs_api_configuration_policy import SQSAPIConfigurationPolicy

logger = get_logger()


class SQSAPI:
    """
    Manage SQS.

    """

    def __init__(self, configuration: SQSAPIConfigurationPolicy, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api

    def provision_queue(self, name, dlq=None):
        """
        Provision sqs queue

        :return:
        """

        sqs_queue = SQSQueue({})
        sqs_queue.region = self.environment_api.region
        sqs_queue.name = name
        sqs_queue.visibility_timeout = "30"
        sqs_queue.maximum_message_size = "262144"
        sqs_queue.message_retention_period = "604800"
        sqs_queue.delay_seconds = "0"
        sqs_queue.tags = {tag["Key"]: tag["Value"] for tag in self.environment_api.configuration.tags}
        sqs_queue.tags["name"] = sqs_queue.name
        if dlq:
            sqs_queue.redrive_policy = "{\"deadLetterTargetArn\":\"" + dlq.arn + "\",\"maxReceiveCount\":3}"
        self.environment_api.aws_api.provision_sqs_queue(sqs_queue)
        return sqs_queue

    def provision_dlq_queue(self, name, queue_names):
        """
        Provision the DLQ queue.

        :return:
        """

        sqs_queue = SQSQueue({})
        sqs_queue.region = self.environment_api.region
        sqs_queue.name = name
        sqs_queue.visibility_timeout = "30"
        sqs_queue.maximum_message_size = "262144"
        sqs_queue.message_retention_period = "604800"
        sqs_queue.delay_seconds = "0"
        sqs_queue.tags = {tag["Key"]: tag["Value"] for tag in self.environment_api.configuration.tags}
        sqs_queue.tags["name"] = sqs_queue.name
        arns = []
        for queue_name in queue_names:
            sqs_queue_image = SQSQueue({})
            sqs_queue_image.region = self.environment_api.region
            sqs_queue_image.account_id = self.environment_api.aws_api.aws_account_id
            sqs_queue_image.name = queue_name
            arns.append(sqs_queue_image.arn)
        sqs_queue.redrive_allow_policy = json.dumps({"redrivePermission": "byQueue",
                                                     "sourceQueueArns": arns})
        self.environment_api.aws_api.provision_sqs_queue(sqs_queue, declarative=True)
        return sqs_queue
