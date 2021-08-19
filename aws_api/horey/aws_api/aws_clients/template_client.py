"""
AWS lambda client to handle lambda service API requests.
"""
import pdb
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.template_entities import TemplateEntity

from horey.h_logger import get_logger
logger = get_logger()


class TemplateClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "Template"
        super().__init__(client_name)

    def get_all_template_entities(self, region=None):
        """
        Get all template_entities in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_template_entities(region)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_template_entities(region)

        return final_result

    def get_region_template_entities(self, region):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.describe_template_entities, "template_entities"):
            obj = TemplateEntity(dict_src)
            final_result.append(obj)

        return final_result

    def provision_template_entity(self, template_entity):
        region_entitys = self.get_region_template_entities(template_entity.region)
        for region_entity in region_entitys:
            if region_entity.get_tagname(ignore_missing_tag=True) == template_entity.get_tagname():
                template_entity.update_from_raw_response(region_entity.dict_src)
                return

        AWSAccount.set_aws_region(template_entity.region)
        response = self.provision_template_entity_raw(template_entity.generate_create_request())
        template_entity.update_from_raw_response(response)

    def provision_template_entity_raw(self, request_dict):
        logger.info(f"Creating template_entity: {request_dict}")
        for response in self.execute(self.client.create_template_entity, "template_entity",
                                     filters_req=request_dict):
            return response
