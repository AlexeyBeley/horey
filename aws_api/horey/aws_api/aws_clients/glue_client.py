"""
AWS glue client.
"""

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

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_tables(
                _region, full_information=full_information
            )

        return final_result

    def get_region_tables(self, region, full_information=True, get_tags=True):
        """
        Standard.

        :param region:
        :param full_information:
        :param get_tags:
        :return:
        """

        final_result = []
        for database in self.get_region_databases(region):
            for dict_src in self.execute(
                    self.get_session_client(region=region).get_tables,
                    "TableList",
                    filters_req={"DatabaseName": database.name},
            ):
                obj = GlueTable(dict_src)
                final_result.append(obj)
                if full_information:
                    pass
                if get_tags:
                    self.get_tags(obj)

        return final_result

    def update_table_information(self, table: GlueTable):
        """
        Table attributes from AWS API.

        :param table:
        :return:
        """

        for dict_src in self.execute(
                self.get_session_client(region=table.region).get_table,
                "Table",
                filters_req={"DatabaseName": table.database_name, "Name": table.name},
                exception_ignore_callback=lambda x: f"Table {table.name} not found"
                                                    in repr(x),
        ):
            table.update_from_raw_response(dict_src)
            table.account_id = self.account_id

            self.get_tags(table)

    def provision_table(self, table: GlueTable):
        """
        Provisioning tags was disabled. There is some stupid bug in AWS API.
        Using the API in a documented way - throws exception.

        :param table:
        :return:
        """

        self.update_table_information(table)
        if table.create_time is not None:
            return

        self.provision_table_raw(table.region, table.generate_create_request())

        self.update_table_information(table)

    def provision_table_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Creating table: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_table, None, raw_data=True, filters_req=request_dict
        ):
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

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_databases(
                _region, full_information=full_information
            )

        return final_result

    def get_region_databases(self, region, full_information=True, get_tags=True):
        """
        Standard.

        :param region:
        :param full_information:
        :param get_tags:
        :return:
        """

        final_result = []
        for dict_src in self.execute(self.get_session_client(region=region).get_databases, "DatabaseList"):
            obj = GlueDatabase(dict_src)
            obj.region = region
            final_result.append(obj)
            if full_information:
                pass
            if get_tags:
                self.get_tags(obj)

        return final_result

    def update_database_information(self, database: GlueDatabase):
        """
        Update database attributes from AWS API.

        :param database:
        :return:
        """

        for dict_src in self.execute(
                self.get_session_client(region=database.region).get_database,
                "Database",
                filters_req={"Name": database.name},
                exception_ignore_callback=lambda x: f"Database {database.name} not found"
                                                    in repr(x),
        ):
            database.update_from_raw_response(dict_src)
            database.account_id = self.account_id

            self.get_tags(database)

    def provision_database(self, database: GlueDatabase):
        """
        Standard.

        :param database:
        :return:
        """

        self.update_database_information(database)
        if database.create_time is not None:
            self.get_tags(database)
            return

        self.provision_database_raw(database.region, database.generate_create_request())
        database.account_id = self.account_id
        self.tag_resource(database)
        self.update_database_information(database)

    def provision_database_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Creating database: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_database, None, raw_data=True, filters_req=request_dict
        ):
            return response

    # endregion
