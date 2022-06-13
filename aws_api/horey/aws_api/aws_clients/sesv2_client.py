"""
AWS lambda client to handle lambda service API requests.
"""
import pdb
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.sesv2_email_identity import SESV2EmailIdentity
from horey.aws_api.aws_services_entities.sesv2_email_template import SESV2EmailTemplate
from horey.aws_api.aws_services_entities.sesv2_configuration_set import SESV2ConfigurationSet

from horey.h_logger import get_logger
logger = get_logger()


class SESV2Client(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """
    UNSUPPORTED_REGIONS = ["ap-east-1", "ap-southeast-3"]

    def __init__(self):
        client_name = "sesv2"
        super().__init__(client_name)

    def get_all_email_identities(self, region=None, full_information=True):
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

    def get_region_email_identities(self, region, full_information=True):
        if region.region_mark in self.UNSUPPORTED_REGIONS:
            return []

        logger.info(f"get_region_email_identities: {region.region_mark}")
        final_result = list()
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.list_email_identities, "EmailIdentities"):
            obj = SESV2EmailIdentity(dict_src)
            final_result.append(obj)

            if full_information:
                self.update_email_identity_information(obj)
        return final_result

    def update_email_identity_information(self, obj: SESV2EmailIdentity):
        response = list(self.execute(self.client.get_email_identity, None,
                                     raw_data=True,
                                     filters_req={"EmailIdentity": obj.name},
                                     exception_ignore_callback=lambda x: "NotFoundException" in repr(x)))
        if len(response) == 0:
            return

        elif len(response) > 1:
            raise RuntimeError(f"Expected to find <= 1 but found {len(response)}")

        dict_src = response[0]
        del dict_src["ResponseMetadata"]

        obj.update_from_raw_response(dict_src)

    def get_all_configuration_sets(self, region=None, full_information=False):
        """
        Get all configuration_sets in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_configuration_sets(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_configuration_sets(region, full_information=full_information)

        return final_result

    def get_region_configuration_sets(self, region, full_information=False):
        if region.region_mark in self.UNSUPPORTED_REGIONS:
            return []

        logger.info(f"get_region_configuration_sets: {region.region_mark}")
        final_result = list()
        AWSAccount.set_aws_region(region)
        for name in self.execute(self.client.list_configuration_sets, "ConfigurationSets"):
            dict_src = list(self.execute(self.client.get_configuration_set, None,
                                         raw_data=True,
                                         filters_req={"ConfigurationSetName": name}))[0]
            del dict_src["ResponseMetadata"]
            obj = SESV2ConfigurationSet(dict_src)
            final_result.append(obj)

            if full_information:
                raise NotImplementedError()

        return final_result

    def get_all_email_templates(self, region=None, full_information=True):
        """
        Get all email_templates in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_email_templates(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_email_templates(region, full_information=full_information)

        return final_result

    def get_region_email_templates(self, region, full_information=True):
        if region.region_mark in self.UNSUPPORTED_REGIONS:
            return []

        logger.info(f"get_region_email_templates: {region.region_mark}")
        final_result = list()
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.list_email_templates, "TemplatesMetadata"):
            obj = SESV2EmailTemplate(dict_src)
            final_result.append(obj)

            if full_information:
                self.update_email_template_information(obj)
        return final_result

    def update_email_template_information(self, obj: SESV2EmailTemplate):
        dict_src = list(self.execute(self.client.get_email_template, None,
                                     raw_data=True,
                                     filters_req={"TemplateName": obj.name}))[0]
        del dict_src["ResponseMetadata"]

        obj.update_from_raw_response(dict_src)

    def get_tags(self, arn):
        for lst_src in self.execute(self.client.list_tags_of_resource, "Tags", filters_req={"ResourceArn": arn}):
            return lst_src

    def provision_configuration_set(self, configuration_set: SESV2ConfigurationSet):
        region_configuration_sets = self.get_region_configuration_sets(configuration_set.region)
        for region_configuration_set in region_configuration_sets:
            if region_configuration_set.name == configuration_set.name:
                configuration_set.update_from_raw_response(region_configuration_set.dict_src)
                return

        AWSAccount.set_aws_region(configuration_set.region)
        self.provision_configuration_set_raw(configuration_set.generate_create_request())

    def provision_configuration_set_raw(self, request_dict):
        logger.info(f"Creating configuration_set: {request_dict}")
        for response in self.execute(self.client.create_configuration_set, None, raw_data=True,
                                     filters_req=request_dict):
            return response
    
    def provision_email_template(self, email_template: SESV2EmailTemplate):
        AWSAccount.set_aws_region(email_template.region)
        self.provision_email_template_raw(email_template.generate_create_request())

    def provision_email_template_raw(self, request_dict):
        for response in self.execute(self.client.update_email_template, None, raw_data=True,
                                     filters_req=request_dict,
                                     exception_ignore_callback=lambda x: "NotFoundException" in repr(x)):
            logger.info(f"Updated email_template: {request_dict}")
            return response
        else:
            logger.info(f"Creating email_template: {request_dict}")
            for response in self.execute(self.client.create_email_template, None, raw_data=True,
                                         filters_req=request_dict,
                                         exception_ignore_callback=lambda x: "NotFoundException" in repr(x)):
                return response

    def provision_email_identity(self, email_identity: SESV2EmailIdentity):
        AWSAccount.set_aws_region(email_identity.region)

        self.update_email_identity_information(email_identity)

        if email_identity.identity_type is not None:
            return

        response = self.provision_email_identity_raw(email_identity.generate_create_request())
        email_identity.update_from_raw_response(response)

    def provision_email_identity_raw(self, request_dict):
        logger.info(f"Creating email_identity: {request_dict}")
        for response in self.execute(self.client.create_email_identity, None, raw_data=True,
                                     filters_req=request_dict):
            del response["ResponseMetadata"]
            return response
