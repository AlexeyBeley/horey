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

    def get_all_tables(self, region=None, full_information=False):
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

    def get_region_tables(self, region, full_information=False):
        """
        Standard.

        @param region:
        @param full_information:
        @return:
        """

        final_result = []
        AWSAccount.set_aws_region(region)
        for table_name in self.execute(self.client.list_tables, "TableNames"):
            obj = DynamoDBTable({"TableName": table_name})
            obj.region = region
            self.update_table_information(obj)
            final_result.append(obj)

            if full_information:
                self.update_table_full_information(obj)

        return final_result

    def update_table_full_information(self, table: DynamoDBTable):
        """
        Get excessive data.

        :param table:
        :return:
        """

        for response in self.execute(self.client.describe_continuous_backups, "ContinuousBackupsDescription",
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
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.describe_endpoints, "Endpoints"):
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

        AWSAccount.set_aws_region(table.region)
        response = self.provision_table_raw(table.generate_create_request())
        table.update_from_raw_response(response)
        return

    def provision_table_raw(self, request_dict):
        """
        Standard.

        @param request_dict:
        @return:
        """

        logger.info(f"Creating table: {request_dict}")
        for response in self.execute(
            self.client.create_table, "TableDescription", filters_req=request_dict
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
                return {value_key: convert_from_dynamodbish_subroutine(value) for value_key, value in sub_obj_src["M"].items()}

            raise ValueError(f"Unsupported type: {type(sub_obj_src)}")

        if not isinstance(obj_src, dict):
            raise ValueError(f"Dict expected: {type(obj_src)}")

        return {key: convert_from_dynamodbish_subroutine(value) for key, value in obj_src.items()}

    def update_table_information(self, table: DynamoDBTable, get_tags=True):
        """
        Standard.

        @param get_tags:
        @param table:
        @return:
        """

        AWSAccount.set_aws_region(table.region)
        for response in self.execute(self.client.describe_table, "Table", filters_req={"TableName": table.name},
                                     exception_ignore_callback=lambda x: "ResourceNotFoundException" in repr(x)):
            table.update_from_raw_response(response)
            if get_tags:
                table.tags = self.get_tags(table, function=self.client.list_tags_of_resource)
                return True

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

        AWSAccount.set_aws_region(table.region)
        return self.dispose_table_raw(table.generate_dispose_request())

    def dispose_table_raw(self, request_dict):
        """
        Standard.

        @param request_dict:
        @return:
        """

        logger.info(f"Disposing table: {request_dict}")
        for response in self.execute(
                self.client.delete_table, "TableDescription", filters_req=request_dict
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
        AWSAccount.set_aws_region(table.region)

        for response in self.execute(self.client.put_item, None, raw_data=True,
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

        AWSAccount.set_aws_region(table.region)

        for response in self.execute(self.client.get_item, "Item",
                                     filters_req=filters_req, instant_raise=True):
            return self.convert_from_dynamodbish(response)
