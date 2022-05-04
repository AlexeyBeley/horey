"""
AWS lambda client to handle lambda service API requests.
"""
import pdb
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.glue_database import GlueDatabase
from horey.aws_api.aws_services_entities.glue_table import GlueTable

from horey.h_logger import get_logger

logger = get_logger()


class GlueClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "glue"
        super().__init__(client_name)

    # region table
    def get_all_tables(self, region=None, full_information=True):
        """
        Get all tables in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_tables(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_tables(region, full_information=full_information)

        return final_result

    def get_region_tables(self, region, full_information=True):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.describe_tables, "tables"):
            obj = GlueTable(dict_src)
            final_result.append(obj)
            if full_information:
                raise NotImplementedError()

        return final_result

    def provision_table(self, table):
        region_tables = self.get_region_tables(table.region)
        for region_table in region_tables:
            if region_table.get_tagname(ignore_missing_tag=True) == table.get_tagname():
                table.update_from_raw_response(region_table.dict_src)
                return

        AWSAccount.set_aws_region(table.region)
        response = self.provision_table_raw(table.generate_create_request())
        table.update_from_raw_response(response)

    def provision_table_raw(self, request_dict):
        logger.info(f"Creating table: {request_dict}")
        for response in self.execute(self.client.create_table, "table",
                                     filters_req=request_dict):
            return response
    # endregion

    # region database
    def get_all_databases(self, region=None, full_information=True):
        """
        Get all databases in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_databases(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_databases(region, full_information=full_information)

        return final_result

    def get_region_databases(self, region, full_information=True):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.describe_databases, "databases"):
            obj = GlueDatabase(dict_src)
            final_result.append(obj)
            if full_information:
                raise NotImplementedError()

        return final_result

    def provision_database(self, database):
        region_databases = self.get_region_databases(database.region)
        for region_database in region_databases:
            if region_database.get_tagname(ignore_missing_tag=True) == database.get_tagname():
                database.update_from_raw_response(region_database.dict_src)
                return

        AWSAccount.set_aws_region(database.region)
        response = self.provision_database_raw(database.generate_create_request())
        database.update_from_raw_response(response)

    def provision_database_raw(self, request_dict):
        logger.info(f"Creating database: {request_dict}")
        for response in self.execute(self.client.create_database, "database",
                                     filters_req=request_dict):
            return response
    # endregion
