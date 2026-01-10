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
                exception_ignore_callback=lambda x: "EntityNotFoundException"
                                                    in repr(x),
        ):
            table.update_from_raw_response(dict_src)
            table.account_id = self.account_id

            return True
        return False

    def provision_table(self, table: GlueTable):
        """
        Provisioning tags was disabled. There is some stupid bug in AWS API.
        Using the API in a documented way - throws exception.

        :param table:
        :return:
        """

        table_current = GlueTable({})
        table_current.region = table.region
        table_current.name = table.name
        table_current.database_name = table.database_name

        if not self.update_table_information(table_current):
            self.provision_table_raw(table.region, table.generate_create_request())

        request = table_current.generate_update_table_request(table)
        if request is not None:
            self.update_table_raw(table.region, request)

        self.update_table_information(table)
        return table

    def provision_table_raw(self, region, request_dict):
        """
        Standard.

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Creating table: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_table, None, raw_data=True, filters_req=request_dict
        ):
            return response
        raise RuntimeError("No response")

    def update_table_raw(self, region, request_dict):
        """
        Standard.

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Updating table: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).update_table, None, raw_data=True, filters_req=request_dict
        ):
            return response
        raise RuntimeError("No response")

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
                try:
                    self.get_tags(obj)
                except Exception as e:
                    if "not found" in str(e):
                        logger.warning(f"Database {obj.name} not found when getting tags")
                    else:
                        raise

        return final_result

    def update_database_information(self, database: GlueDatabase) -> bool:
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
            return True
        return False

    def provision_database(self, database: GlueDatabase):
        """
        Standard.

        :param database:
        :return:
        """

        database_current = GlueDatabase({})
        database_current.name = database.name
        database_current.region = database.region
        if not self.update_database_information(database_current):
            self.provision_database_raw(database.region, database.generate_create_request())

        tag_request, untag_request = database_current.generate_tagging_requests(database)
        if tag_request:
            self.tag_resource_raw(database.region, tag_request)
        if untag_request:
            self.untag_resource_raw(database.region, untag_request)

        self.update_database_information(database)
        return database

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

        return True

    # endregion

    def dispose_database(self, database: GlueDatabase):
        """
        Standard.

        :param database:
        :return:
        """

        if not self.update_database_information(database):
            return True
        return self.dispose_database_raw(database.region, {"CatalogId": database.catalog_id, "Name": database.name})

    def dispose_database_raw(self, region, request_dict):
        """
        response = client.delete_database(
        CatalogId='string',
        Name='string' # required
        )

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Disposing database: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).delete_database, None, raw_data=True, filters_req=request_dict
        ):
            return response

    def dispose_table(self, table: GlueTable):
        """
        Standard.

        :param table:
        :return:
        """

        if not self.update_table_information(table):
            return True

        return self.dispose_table_raw(table.region, {"DatabaseName": table.database_name, "TablesToDelete": [table.name]})

    def dispose_table_raw(self, region, request_dict):
        """
        Standard.

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Disposing table: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).delete_table, None, raw_data=True, filters_req=request_dict
        ):
            return response

        raise ValueError(f"Table not found: {request_dict}")

    def tag_resource_raw(self, region, request_dict):
        """
        Standard.

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Tagging resource: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).tag_resource ,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            self.clear_cache(GlueDatabase)
            self.clear_cache(GlueTable)
            return response


        raise ValueError(f"Tag not found: {request_dict}")

    def untag_resource_raw(self, region, request_dict):
        """
        Standard.

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Untagging resource: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).untag_resource,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            self.clear_cache(GlueDatabase)
            self.clear_cache(GlueTable)
            return response


        raise ValueError(f"Tag not found: {request_dict}")

    # pylint: disable = arguments-differ
    def get_tags(self, obj, function=None, instant_raise=False):
        """
        Get tags for resource.

        :param instant_raise:
        :param obj:
        :param function:
        :return:
        """

        logger.info(f"Getting resource tags: {obj.arn}")
        ret = list(
            self.execute(self.get_session_client(obj.region).get_tags, "Tags", filters_req={"ResourceArn": obj.arn}, instant_raise=instant_raise)
        )

        obj.tags = ret[0] if ret else {}
        return ret
