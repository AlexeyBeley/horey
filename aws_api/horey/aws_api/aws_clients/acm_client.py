"""
AWS lambda client to handle lambda service API requests.
"""
import pdb
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.acm_certificate import ACMCertificate

from horey.h_logger import get_logger
logger = get_logger()


class ACMClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    Validate fingerprint
    openssl pkcs8 -in file_name.pem -inform PEM -outform DER -topk8 -nocrypt | openssl sha1 -c
    """

    def __init__(self):
        client_name = "acm"
        super().__init__(client_name)

    def get_all_certificates(self, region=None):
        """
        Get all acm_certificates in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_certificates(region)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_certificates(region)

        return final_result

    def get_region_certificates(self, region):
        final_result = list()
        AWSAccount.set_aws_region(region)

        for dict_src_arn in self.execute(self.client.list_certificates, "CertificateSummaryList"):
            obj = self.get_certificate(dict_src_arn["CertificateArn"])
            final_result.append(obj)

        return final_result

    def get_certificate(self, arn):
        filters_req = {"CertificateArn": arn}
        certs_dicts = list(self.execute(self.client.describe_certificate, "Certificate", filters_req=filters_req))
        if len(certs_dicts) == 0:
            return None

        if len(certs_dicts) > 1:
            raise ValueError(arn)

        return ACMCertificate(certs_dicts[0])

    def provision_certificate(self, certificate):
        region_certificates = self.get_region_certificates(certificate.region)
        for region_certificate in region_certificates:
            if certificate.domain_name == region_certificate.domain_name:
                certificate.update_from_raw_response(region_certificate.dict_src)
                return certificate.arn

        AWSAccount.set_aws_region(certificate.region)
        response_arn = self.provision_certificate_raw(certificate.generate_create_request())
        certificate.arn = response_arn

        region_certificates = self.get_region_certificates(certificate.region)
        for region_certificate in region_certificates:
            if region_certificate.arn == certificate.arn:
                certificate.update_from_raw_response(region_certificate.dict_src)
                break

    def provision_certificate_raw(self, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Creating certificate: {request_dict}")
        for response in self.execute(self.client.request_certificate, "CertificateArn",
                                     filters_req=request_dict):
            return response