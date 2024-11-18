"""
AWS lambda client to handle lambda service API requests.
"""

from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.dynamodb_table import DynamoDBTable
from horey.aws_api.aws_services_entities.dynamodb_endpoint import DynamoDBEndpoint

from horey.h_logger import get_logger

logger = get_logger()


class DynamoDBClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "dynamodb"
        super().__init__(client_name)

    # pylint: disable= too-many-arguments
    def yield_tables(self, region=None, update_info=False, filters_req=None, get_tags=True, full_information=True):
        """
        Yield tables

        :return:
        """

        regional_fetcher_generator = self.yield_tables_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            DynamoDBTable,
                                                            update_info=update_info,
                                                            get_tags_callback=lambda _obj: self.get_tags(_obj,
                                                                                                         function=self.get_session_client(
                                                                                                             region=region).list_tags_of_resource) if get_tags else None,
                                                            full_information_callback=self.update_table_full_information if full_information else None,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_tables_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        for str_name in self.execute(
                self.get_session_client(region=region).list_tables, "TableNames",
                filters_req=filters_req,
                exception_ignore_callback=lambda error: "RepositoryNotFoundException"
                                                        in repr(error)
        ):
            yield from self.execute(self.get_session_client(region=region).describe_table, "Table",
                                    filters_req={"TableName": str_name},
                                    exception_ignore_callback=lambda x: "ResourceNotFoundException" in repr(x))

    def get_all_tables(self, region=None, full_information=False):
        """
        Get all tables in all regions.
        :return:
        """

        return list(self.yield_tables(region=region, full_information=full_information))

    def get_region_tables(self, region, full_information=False):
        """
        Standard.

        @param region:
        @param full_information:
        @return:
        """

        return list(self.yield_tables(region=region, full_information=full_information))

    def update_table_full_information(self, table: DynamoDBTable):
        """
        Get excessive data.

        :param table:
        :return:
        """

        for response in self.execute(self.get_session_client(region=table.region).describe_continuous_backups,
                                     "ContinuousBackupsDescription",
                                     filters_req={"TableName": table.name}):
            table.continuous_backups = response

    def get_all_endpoints(self, region=None, full_information=False):
        """
        Get all endpoints in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_endpoints(region, full_information=full_information)

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_endpoints(
                _region, full_information=full_information
            )

        return final_result

    def get_region_endpoints(self, region, full_information=False):
        """
        Standard.

        @param region:
        @param full_information:
        @return:
        """

        final_result = []
        for dict_src in self.execute(self.get_session_client(region=region).describe_endpoints, "Endpoints"):
            obj = DynamoDBEndpoint(dict_src)
            final_result.append(obj)

            if full_information:
                raise NotImplementedError()

        return final_result

    def provision_table(self, table: DynamoDBTable):
        """
        WARNING! Does not support Updating only creation

        @param table:
        @return:
        """

        current_table = DynamoDBTable({})
        current_table.region = table.region
        current_table.name = table.name
        if self.update_table_information(current_table, get_tags=True):
            self.update_table_information(table)
            return

        response = self.provision_table_raw(table.region, table.generate_create_request())
        table.update_from_raw_response(response)
        return

    def provision_table_raw(self, region, request_dict):
        """
        Standard.

        @param request_dict:
        @return:
        """

        logger.info(f"Creating table: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_table, "TableDescription", filters_req=request_dict
        ):
            return response

    @staticmethod
    def convert_to_dynamodbish(obj_src):
        """
        Convert to dynamodb format.

        :param obj_src:
        :return:
        """

        def convert_to_dynamodbish_subroutine(sub_obj_src):
            """
            Recursive Subroutine.

            :param sub_obj_src:
            :return:
            """

            if isinstance(sub_obj_src, dict):
                return {"M": {key: convert_to_dynamodbish_subroutine(value) for key, value in sub_obj_src.items()}}
            if isinstance(sub_obj_src, str):
                return {"S": sub_obj_src}
            if isinstance(sub_obj_src, int):
                return {"N": str(sub_obj_src)}

            raise ValueError(f"Unsupported type: {type(sub_obj_src)}")

        if not isinstance(obj_src, dict):
            raise ValueError(f"Dict expected: {type(obj_src)}")

        return {key: convert_to_dynamodbish_subroutine(value) for key, value in obj_src.items()}

    @staticmethod
    def convert_from_dynamodbish(obj_src):
        """
        Convert from dynamodb format.

        :param obj_src:
        :return:
        """

        def convert_from_dynamodbish_subroutine(sub_obj_src):
            """
            Recursive Subroutine.

            :param sub_obj_src:
            :return:
            """

            if not isinstance(sub_obj_src, dict):
                return sub_obj_src

            if len(sub_obj_src) != 1:
                raise ValueError(f"Value must be of type S/M/D...: '{sub_obj_src}'")

            if "S" in sub_obj_src:
                return sub_obj_src["S"]
            if "N" in sub_obj_src:
                return int(sub_obj_src["N"])
            if "M" in sub_obj_src:
                return {value_key: convert_from_dynamodbish_subroutine(value) for value_key, value in
                        sub_obj_src["M"].items()}

            raise ValueError(f"Unsupported type: {type(sub_obj_src)}")

        if not isinstance(obj_src, dict):
            raise ValueError(f"Dict expected: {type(obj_src)}")

        return {key: convert_from_dynamodbish_subroutine(value) for key, value in obj_src.items()}

    def update_table_information(self, table: DynamoDBTable, get_tags=True, raise_if_not_found=False):
        """
        Standard.

        :param table:
        :param get_tags:
        :param raise_if_not_found:
        :return:
        """

        for response in self.execute(self.get_session_client(region=table.region).describe_table, "Table",
                                     filters_req={"TableName": table.name},
                                     exception_ignore_callback=lambda x: "ResourceNotFoundException" in repr(x)):
            table.update_from_raw_response(response)
            if get_tags:
                table.tags = self.get_tags(table,
                                           function=self.get_session_client(region=table.region).list_tags_of_resource)
            return True

        if raise_if_not_found:
            raise RuntimeError(
                f"Was not able to find DynamoDB Table '{table.name}' in region {table.region.region_mark}")

        return False

    def dispose_table(self, table: DynamoDBTable, disable_deletion_protection=False):
        """
        Standard.

        @param table:
        @param disable_deletion_protection:
        @return:
        """
        if not self.update_table_information(table):
            return True

        if table.deletion_protection_enabled and not disable_deletion_protection:
            raise RuntimeError("deletion_protection is enabled")

        return self.dispose_table_raw(table.region, table.generate_dispose_request())

    def dispose_table_raw(self, region, request_dict):
        """
        Standard.

        @param request_dict:
        @return:
        """

        logger.info(f"Disposing table: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).delete_table, "TableDescription", filters_req=request_dict
        ):
            return response

    def put_item(self, table: DynamoDBTable, item):
        """
        Put item- a normal dict. Automatically converted to dynamodbish.

        :param table:
        :param item:
        :return:
        """

        dynamodbish_item = self.convert_to_dynamodbish(item)
        filters_req = {"TableName": table.name,
                       "Item": dynamodbish_item}

        for response in self.execute(self.get_session_client(region=table.region).put_item, None, raw_data=True,
                                     filters_req=filters_req, instant_raise=True):
            return response

    def get_item(self, table: DynamoDBTable, dict_key):
        """
        get item- a dynamodbish dict is automatically converted to normal dict.

        :param table:
        :param dict_key:
        :return:
        """

        filters_req = {"TableName": table.name,
                       "Key": self.convert_to_dynamodbish(dict_key)}

        for response in self.execute(self.get_session_client(region=table.region).get_item, "Item",
                                     filters_req=filters_req, instant_raise=True):
            return self.convert_from_dynamodbish(response)

    def scan(self, table: DynamoDBTable):
        """
        Standard.

        :param table:
        :return:
        """

        for response in self.execute(self.get_session_client(region=table.region).scan, "Items",
                                     filters_req={"TableName": table.name},
                                     ):
            yield self.convert_from_dynamodbish(response)

    def delete_item(self, table: DynamoDBTable, item):
        """
        Put item- a normal dict. Automatically converted to dynamodbish.

        :param table:
        :param item:
        :return:
        """

        dynamodbish_item = self.convert_to_dynamodbish(item)
        filters_req = {"TableName": table.name,
                       "Key": dynamodbish_item}

        logger.info(f"Deleting dynamoDB item: '{filters_req}'")
        for response in self.execute(self.get_session_client(region=table.region).delete_item, None, raw_data=True,
                                     filters_req=filters_req, instant_raise=True):
            return response
