"""
AWS sts client to handle lambda service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.h_logger import get_logger

logger = get_logger()


class STSClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "sts"
        super().__init__(client_name)

    def get_account(self):
        """
        Standard.

        :return:
        """

        for response in self.execute(self.client.get_caller_identity, "Account"):
            return response
