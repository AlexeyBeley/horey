"""
AWS lambda client to handle lambda service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.ssm_parameter import SSMParameter

from horey.h_logger import get_logger

logger = get_logger()


class SSMClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "ssm"
        super().__init__(client_name)

    def get_region_parameter(self, region, name):
        """
        Get ssm parameter

        :param region:
        :param name:
        :return:
        """

        AWSAccount.set_aws_region(region)
        filters_req = {"Name": name}

        raw_data = list(
            self.execute(
                self.client.get_parameter, "Parameter", filters_req=filters_req
            )
        )
        if len(raw_data) != 1:
            raise RuntimeError(f"Expected single response for param '{name}', received {len(raw_data)} items")

        return SSMParameter(raw_data[0])
