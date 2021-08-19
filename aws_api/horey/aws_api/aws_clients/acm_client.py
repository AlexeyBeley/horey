"""
AWS lambda client to handle lambda service API requests.
"""
import pdb
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.acm_certificate import ACMCertificate

from horey.h_logger import get_logger
logger = get_logger()


class TemplateClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "ACM"
        super().__init__(client_name)

    def get_all_acm_certificates(self, region=None):
        """
        Get all acm_certificates in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_acm_certificates(region)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_acm_certificates(region)

        return final_result

    def get_region_acm_certificates(self, region):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.describe_acm_certificates, "acm_certificates"):
            obj = ACMCertificate(dict_src)
            final_result.append(obj)

        return final_result

    def provision_acm_certificate(self, acm_certificate):
        region_certificates = self.get_region_acm_certificates(acm_certificate.region)
        for region_certificate in region_certificates:
            if region_certificate.get_tagname(ignore_missing_tag=True) == acm_certificate.get_tagname():
                acm_certificate.update_from_raw_response(region_certificate.dict_src)
                return

        AWSAccount.set_aws_region(acm_certificate.region)
        response = self.provision_acm_certificate_raw(acm_certificate.generate_create_request())
        acm_certificate.update_from_raw_response(response)

    def provision_acm_certificate_raw(self, request_dict):
        logger.info(f"Creating acm_certificate: {request_dict}")
        for response in self.execute(self.client.create_acm_certificate, "acm_certificate",
                                     filters_req=request_dict):
            return response
