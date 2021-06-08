"""
AWS clietn to handle service API requests.
"""
import pdb


from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.h_logger import get_logger


logger = get_logger()


class SNSClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "sns"
        super().__init__(client_name)

    def raw_publish(self, topic_arn, message):
        filters_req = {"TopicArn": topic_arn, "Message": ":thumbsup:" + "Ignore this message", "Subject": "Zabbix test alert"}
        # state_dict = {"Ok": ":thumbsup:", "Info": ":information_source:", "Severe": ":exclamation:"}

        for response in self.execute(self.client.publish, "MessageId", filters_req=filters_req):
            return response
