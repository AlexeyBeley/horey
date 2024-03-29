"""
AWS client to handle service API requests.
"""

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.elasticsearch_domain import ElasticsearchDomain
from horey.h_logger import get_logger


logger = get_logger()


class ElasticsearchClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "es"
        super().__init__(client_name)

    def get_all_domains(self):
        """
        Standard.

        :return:
        """

        final_result = []
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_domains(region)
        return final_result

    def get_region_domains(self, region):
        """
        Standard.

        :param region:
        :return:
        """

        final_result = []
        AWSAccount.set_aws_region(region)
        domain_names = []
        for response in self.execute(self.client.list_domain_names, "DomainNames"):
            domain_names.append(response["DomainName"])

        if not domain_names:
            return final_result

        filters_req = {"DomainNames": domain_names}
        for response in self.execute(
            self.client.describe_elasticsearch_domains,
            "DomainStatusList",
            filters_req=filters_req,
        ):
            obj = ElasticsearchDomain(response)
            final_result.append(obj)

        return final_result

    def raw_update_elasticsearch_domain_config(self, request, region=None):
        """
        Update from server response.

        :param request:
        :param region:
        :return:
        """

        if region is not None:
            AWSAccount.set_aws_region(region)

        for response in self.execute(
            self.client.update_elasticsearch_domain_config,
            "DomainConfig",
            filters_req=request,
        ):
            return response
