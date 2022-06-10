"""
AWS lambda client to handle lambda service API requests.
"""
import pdb
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.sesv2_email_identity import SESV2EmailIdentity

from horey.h_logger import get_logger
logger = get_logger()


class SESV2Client(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "sesv2"
        super().__init__(client_name)

    def get_all_email_identities(self, region=None, full_information=False):
        """
        Get all email_identities in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_email_identities(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_email_identities(region, full_information=full_information)

        return final_result

    def get_region_email_identities(self, region, full_information=False):
        final_result = list()
        AWSAccount.set_aws_region(region)
        pdb.set_trace()
        for table_name in list(self.execute(self.client.list_email_identities, "EmailIdentities")):
            ret = list(self.execute(self.client.describe_table, "Table", filters_req={"TableName": table_name}))
            obj = SESV2EmailIdentity(ret[0])
            final_result.append(obj)
            obj.tags = self.get_tags(obj.arn)

            if full_information:
                raise NotImplementedError()

        return final_result

    def get_all_endpoints(self, region=None, full_information=False):
        pdb.set_trace()
        ret = list(self.execute(self.client.list_configuration_sets, "ConfigurationSets"))
        ret = list(self.execute(self.client.list_email_identities, "EmailIdentities"))
        ret = list(self.execute(self.client.list_email_templates, None, raw_data=True))

        ret = list(self.execute(self.client.list_contact_lists, None, raw_data=True))
        ret = list(self.execute(self.client.list_contacts, None, raw_data=True))

        ret = list(self.execute(self.client.list_custom_verification_email_templates, None, raw_data=True))
        ret = list(self.execute(self.client.list_dedicated_ip_pools, None, raw_data=True))
        ret = list(self.execute(self.client.list_deliverability_test_reports, None, raw_data=True))
        ret = list(self.execute(self.client.list_domain_deliverability_campaigns, None, raw_data=True))
        ret = list(self.execute(self.client.list_import_jobs, None, raw_data=True))
        ret = list(self.execute(self.client.list_suppressed_destinations, None, raw_data=True))
        ret = list(self.execute(self.client.list_tags_for_resource, None, raw_data=True))
        """
        Get all endpoints in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_endpoints(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_endpoints(region, full_information=full_information)

        return final_result

    def get_region_endpoints(self, region, full_information=False):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.describe_endpoints, "Endpoints"):
            obj = SESV2Endpoint(dict_src)
            final_result.append(obj)

            if full_information:
                raise NotImplementedError()

        return final_result

    def get_tags(self, arn):
        for lst_src in self.execute(self.client.list_tags_of_resource, "Tags", filters_req={"ResourceArn": arn}):
            return lst_src

    def provision_table(self, table: SESV2Table):
        region_template_entities = self.get_region_tables(table.region)
        for region_table in region_template_entities:
            if region_table.name == table.name:
                table.update_from_raw_response(region_table.dict_src)
                return

        AWSAccount.set_aws_region(table.region)
        response = self.provision_table_raw(table.generate_create_request())
        table.update_from_raw_response(response)

    def provision_table_raw(self, request_dict):
        logger.info(f"Creating table: {request_dict}")
        for response in self.execute(self.client.create_table, "TableDescription",
                                     filters_req=request_dict):
            return response
