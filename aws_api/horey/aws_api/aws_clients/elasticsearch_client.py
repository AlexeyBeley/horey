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
        self.request_key_to_attribute_mapping = {"DomainName": "name", "TagList": "tags"}

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

    def cancel_elasticsearch_service_software_update(self, domain: ElasticsearchDomain):
        """
        Cancel update

        :param domain:
        :return:
        """

        logger.info(f"Canceling Elasticsearch Domain Update: {domain.name}")
        request = domain.generate_request(["DomainName"],
                                          request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)

        for response in self.execute(
                self.get_session_client(region=domain.region).cancel_elasticsearch_service_software_update,
                None, raw_data=True,
                filters_req=request,
        ):
            return response

    def get_max_opensearch_version(self, region):
        """
        Standard.

        :return:
        """

        raw_versions = self.get_region_versions(region)
        versions = [str_version.replace("OpenSearch_", "") for str_version in raw_versions if
                    "OpenSearch_" in str_version]
        max_major = max(int(version.split(".")[0]) for version in versions)
        all_max_major_minors = [int(version.split(".")[1]) for version in versions if
                                version.startswith(f"{max_major}.")]

        composed_version = f"OpenSearch_{max_major}.{max(all_max_major_minors)}"
        if composed_version not in raw_versions:
            raise ValueError(f"{raw_versions=}, {composed_version=}")
        return composed_version

    def get_region_versions(self, region):
        """
        Standard.

        :param region:
        :return:
        """

        return list(self.execute(
            self.get_session_client(region=region).list_elasticsearch_versions,
            "ElasticsearchVersions"
        ))

    def update_domain_information(self, domain: ElasticsearchDomain):
        """
        Standard.

        :param domain:
        :return:
        """
        domain.domain_processing_status = "NONE"
        for regional_domain in self.get_region_domains(domain.region):
            if regional_domain.name == domain.name:
                domain.update_from_raw_response(regional_domain.dict_src)
                return True
        return False

    def provision_domain(self, domain: ElasticsearchDomain):
        """
        Standard.

        :param domain:
        :return:
        """
        current_domain = ElasticsearchDomain({})
        current_domain.region = domain.region
        current_domain.name = domain.name
        if not self.update_domain_information(current_domain):
            request = domain.generate_request(["DomainName", "ElasticsearchVersion", "ElasticsearchClusterConfig", "EBSOptions", "TagList"],
                                              optional=["AccessPolicies", "SnapshotOptions", "VPCOptions", "CognitoOptions", "EncryptionAtRestOptions",
                                                        "NodeToNodeEncryptionOptions", "AdvancedOptions", "LogPublishingOptions", "DomainEndpointOptions",
                                                        "AdvancedSecurityOptions", "AutoTuneOptions"],
                                              request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)

            self.create_elasticsearch_domain_raw(domain.region, request)
            self.wait_for_status(domain, self.update_domain_information, [domain.State.ACTIVE],
                                 [domain.State.CREATING,
                                  domain.State.UPDATING_ENGINE_VERSION,
                                  domain.State.UPDATING_SERVICE_SOFTWARE,
                                  domain.State.MODIFYING],
                                 [domain.State.DELETING,
                                  domain.State.ISOLATED
                                  ], timeout=60*60)
            return True

        if current_domain.domain_processing_status != "Active":
            raise ValueError(current_domain.domain_processing_status)
        self.update_domain_information(domain)

        return True

    def create_elasticsearch_domain_raw(self, region, request):
        """
        Standard.

        :param region:
        :param request:
        :return:
        """

        logger.info(f"Creating opensearch domain: {request['DomainName']}")
        for response in self.execute(
                self.get_session_client(region=region).create_elasticsearch_domain,
                None, raw_data=True, filters_req=request
        ):
            return response

    def dispose_domain(self, domain):
        """
        Standard.

        :param domain:
        :return:
        """

        logger.info(f"Disposing opensearch domain: {domain.name}")

        request = domain.generate_request(["DomainName"],
                                          request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)

        for _ in self.execute(
                self.get_session_client(region=domain.region).delete_elasticsearch_domain,
                None, raw_data=True, filters_req=request
        ):
            break

        self.wait_for_status(domain, self.update_domain_information, [domain.State.NONE],
                             [domain.State.DELETING],
                             [domain.State.CREATING,
                              domain.State.ISOLATED,
                              domain.State.UPDATING_ENGINE_VERSION,
                              domain.State.UPDATING_SERVICE_SOFTWARE,
                              domain.State.MODIFYING
                              ], timeout=60 * 60)
