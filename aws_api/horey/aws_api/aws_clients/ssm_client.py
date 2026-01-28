"""
AWS lambda client to handle lambda service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.aws_services_entities.ssm_parameter import SSMParameter

from horey.h_logger import get_logger

logger = get_logger()


class SSMClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self, aws_account=None):
        client_name = "ssm"
        super().__init__(client_name, aws_account=aws_account)

    def get_region_parameter(self, region, name):
        """
        Get ssm parameter

        :param region:
        :param name:
        :return:
        """

        filters_req = {"Name": name}

        raw_data = list(
            self.execute(
                self.get_session_client(region=region).get_parameter, "Parameter", filters_req=filters_req
            )
        )
        if len(raw_data) != 1:
            raise RuntimeError(f"Expected single response for param '{name}', received {len(raw_data)} items")

        return SSMParameter(raw_data[0])

    def describe_parameters_raw(self, region, filters_req=None):
        """
        Get ssm parameter
        filters_req = {"ParameterFilters": [{
            'Key': 'Name',
            'Option': 'BeginsWith',
            'Values': [
                '/aws/service/canonical/ubuntu/server',
            ]
        }]}
        all_params = self.environment_api.aws_api.ssm_client.describe_parameters_raw(region=self.environment_api.region, filters_req=filters_req)

        :param filters_req:
        :param region:
        :return:
        """

        return list(
            self.execute(
                self.get_session_client(region=region).describe_parameters, "Parameters", filters_req=filters_req
            )
        )
