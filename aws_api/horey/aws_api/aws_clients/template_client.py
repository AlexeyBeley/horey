"""
AWS lambda client to handle lambda service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.template_entity import TemplateEntity

from horey.h_logger import get_logger

logger = get_logger()


class TemplateClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self, aws_account=None):
        client_name = "Template"
        super().__init__(client_name, aws_account=aws_account)

    def get_all_template_entities(self, region=None, full_information=True):
        """
        Get all template_entities in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_template_entities(
                region, full_information=full_information
            )

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_template_entities(
                _region, full_information=full_information
            )

        return final_result

    def get_region_template_entities(self, region, full_information=True):
        """
        Get region objects.

        :param region:
        :param full_information:
        :return:
        """

        final_result = []
        for dict_src in self.execute(
                self.get_session_client(region=region).describe_template_entities, "template_entities"
        ):
            obj = TemplateEntity(dict_src)
            final_result.append(obj)
            if full_information:
                raise NotImplementedError()

        return final_result

    def provision_template_entity(self, template_entity):
        """
        Provision object.

        :param template_entity:
        :return:
        """

        region_template_entities = self.get_region_template_entities(
            template_entity.region
        )
        for region_template_entity in region_template_entities:
            if (
                    region_template_entity.get_tagname(ignore_missing_tag=True)
                    == template_entity.get_tagname()
            ):
                template_entity.update_from_raw_response(
                    region_template_entity.dict_src
                )
                return

        response = self.provision_template_entity_raw(template_entity.region,
                                                      template_entity.generate_create_request()
                                                      )
        template_entity.update_from_raw_response(response)

    def provision_template_entity_raw(self, region, request_dict):
        """
        Provision from request dict

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Creating template_entity: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_template_entity,
                "template_entity",
                filters_req=request_dict,
        ):
            return response
