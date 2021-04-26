"""
AWS client to handle cloud watch logs.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.cloud_watch_metric import CloudWatchMetric
from horey.aws_api.base_entities.aws_account import AWSAccount

import pdb
class CloudWatchClient(Boto3Client):
    """
    Client to work with cloud watch logs API.
    """

    def __init__(self):
        client_name = "cloudwatch"
        super().__init__(client_name)

    def yield_cloud_watch_metrics(self):
        """
        Yields metrics - made to handle large amounts of data, in order to prevent the OOM collapse.
        :return:
        """

        for response in self.execute(self.client.list_metrics, "Metrics"):
            yield response
