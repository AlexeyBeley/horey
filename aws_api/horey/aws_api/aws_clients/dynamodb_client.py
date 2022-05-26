"""
AWS lambda client to handle lambda service API requests.
"""
import pdb
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.dynamodb_table import DynamoDBTable

from horey.h_logger import get_logger
logger = get_logger()


class DynamoDBClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "dynamodb"
        super().__init__(client_name)
        pdb.set_trace()
        ret = list(self.execute(self.client.get_databases, None, raw_data=True))
        ret = list(self.execute(self.client.list_tables, None, raw_data=True))
        """
        list_exports()
        list_global_tables()
        list_tables()
        list_tags_of_resource()
        describe_backup()
describe_continuous_backups()
describe_contributor_insights()
describe_endpoints()
describe_export()
describe_global_table()
describe_global_table_settings()
describe_kinesis_streaming_destination()
describe_limits()
describe_table()
describe_table_replica_auto_scaling()
describe_time_to_live()
        """


    def get_all_template_entities(self, region=None, full_information=True):
        """
        Get all template_entities in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_template_entities(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_template_entities(region, full_information=full_information)

        return final_result

    def get_region_template_entities(self, region, full_information=True):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.describe_template_entities, "template_entities"):
            obj = DynamoDBEntity(dict_src)
            final_result.append(obj)
            if full_information:
                raise NotImplementedError()

        return final_result

    def provision_template_entity(self, template_entity):
        region_template_entities = self.get_region_template_entities(template_entity.region)
        for region_template_entity in region_template_entities:
            if region_template_entity.get_tagname(ignore_missing_tag=True) == template_entity.get_tagname():
                template_entity.update_from_raw_response(region_template_entity.dict_src)
                return

        AWSAccount.set_aws_region(template_entity.region)
        response = self.provision_template_entity_raw(template_entity.generate_create_request())
        template_entity.update_from_raw_response(response)

    def provision_template_entity_raw(self, request_dict):
        logger.info(f"Creating template_entity: {request_dict}")
        for response in self.execute(self.client.create_template_entity, "template_entity",
                                     filters_req=request_dict):
            return response
