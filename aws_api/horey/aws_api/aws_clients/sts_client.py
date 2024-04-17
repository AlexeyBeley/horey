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

    def get_account(self, region=None):
        """
        Standard.

        :return:
        """

        for response in self.execute(self.get_session_client(region=region).get_caller_identity, "Account"):
            return response

    def decode_authorization_message(self, txt_message, region=None):
        """
        Decode encoded message.

        :param region:
        :param txt_message:
        :return:
        """

        filters_req = {"EncodedMessage": txt_message}
        for response in self.execute(self.get_session_client(region=region).decode_authorization_message,
                                     "DecodedMessage", filters_req=filters_req):
            return response
