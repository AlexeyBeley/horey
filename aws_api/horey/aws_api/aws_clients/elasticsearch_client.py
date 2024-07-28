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
        domain_names = []
        for response in self.execute(self.get_session_client(region=region).list_domain_names, "DomainNames"):
            domain_names.append(response["DomainName"])

        if not domain_names:
            return final_result

        filters_req = {"DomainNames": domain_names}
        for response in self.execute(
                self.get_session_client(region=region).describe_elasticsearch_domains,
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

        logger.info(f"Updating Elasticsearch Domain: {request}")

        for response in self.execute(
                self.get_session_client(region=region).update_elasticsearch_domain_config,
                "DomainConfig",
                filters_req=request,
        ):
            return response
