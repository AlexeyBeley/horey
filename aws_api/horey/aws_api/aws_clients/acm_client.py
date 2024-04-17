"""
AWS lambda client to handle lambda service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client

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

    def yield_certificates(self, region=None, update_info=False):
        """
        Yield certificates

        :return:
        """

        regional_fetcher_generator = self.yield_certificates_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                                    ACMCertificate,
                                                                    update_info=update_info,
                                                                    get_tags_callback=self.fetch_certificate_tags,
                                                                    regions=[region] if region else None)

    def get_all_certificates(self, region=None, update_info=False):
        """
        Get all acm_certificates in all regions.

        :return:
        """

        return list(self.yield_certificates(region=region, update_info=update_info))

    def yield_certificates_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src_arn in self.execute(
                self.get_session_client(region=region).list_certificates, "CertificateSummaryList",
                filters_req=filters_req
        ):
            arn = dict_src_arn["CertificateArn"]
            _filters_req = {"CertificateArn": arn}
            certs_dicts = list(
                self.execute(
                    self.get_session_client(region=region).describe_certificate, "Certificate", filters_req=_filters_req
                )
            )

            if len(certs_dicts) == 0:
                return None

            if len(certs_dicts) > 1:
                raise ValueError(arn)

            yield certs_dicts[0]
        return None

    def get_region_certificates(self, region):
        """
        Get list.

        :param region:
        :return:
        """

        return [ACMCertificate(dict_src) for dict_src in self.yield_certificates_raw(region)]

    def fetch_certificate_tags(self, cert):
        """
        Get extended info.

        :param cert:
        :return:
        """
        filters_req = {"CertificateArn": cert.arn}
        cert.tags = list(
            self.execute(
                self.get_session_client(region=cert.region).list_tags_for_certificate, "Tags", filters_req=filters_req
            )
        )

    def get_certificate(self, arn):
        """
        Get single certificate.

        :param arn:
        :return:
        """

        region = self.get_region_from_arn(arn)
        filters_req = {"CertificateArn": arn}
        certs_dicts = list(
            self.execute(
                self.get_session_client(region=region).describe_certificate, "Certificate", filters_req=filters_req,
                exception_ignore_callback=lambda x: "ResourceNotFoundException" in repr(x)
            )
        )

        if len(certs_dicts) == 0:
            return None

        if len(certs_dicts) > 1:
            raise ValueError(arn)

        obj = ACMCertificate(certs_dicts[0])

        return obj

    def provision_certificate(self, certificate):
        """
        Provision certificate.

        :param certificate:
        :return:
        """
        if not certificate.tags:
            raise ValueError(
                "Can not provision certificates without unique tags set. Look at certificate.generate_name_tag")
        try:
            current_certificate = self.get_certificate_by_tags(certificate.region,
                                                               {"name": tag["Value"] for tag in certificate.tags if
                                                                tag["Key"] == "name"}, ignore_missing_tag=True)
            if current_certificate.domain_name == certificate.domain_name:
                certificate.update_from_raw_response(current_certificate.dict_src)
                return certificate.arn
        except Exception as inst_error:
            if "ResourceNotFoundError" not in repr(inst_error):
                raise

        response_arn = self.provision_certificate_raw(certificate.region,
                                                      certificate.generate_create_request()
                                                      )
        certificate.arn = response_arn

        self.clear_cache(ACMCertificate)

        return response_arn

    def provision_certificate_raw(self, region, request_dict):
        """
        Returns ARN
        """
        logger.info(f"Creating certificate: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).request_certificate, "CertificateArn", filters_req=request_dict
        ):
            return response

    def get_certificate_by_tags(self, region, dict_tags, ignore_missing_tag=False, update_info=False):
        """
        Find certificate by tags

        :param region:
        :param dict_tags:
        :param ignore_missing_tag:
        :param update_info:
        :return:
        """
        ret = []
        for cert in self.yield_certificates(region, update_info=update_info):
            for tag_key, tag_value in dict_tags.items():
                if (
                        cert.get_tag(tag_key, ignore_missing_tag=ignore_missing_tag)
                        != tag_value
                ):
                    break
            else:
                ret.append(cert)

        if len(ret) > 1:
            raise ValueError(
                f"Found more then 1 certificate in region '{str(region)}' with tags: {dict_tags}: {[cert.arn for cert in ret]}"
            )

        try:
            return ret[0]
        except IndexError as error_instance:
            raise self.ResourceNotFoundError(
                f"No certificates found in region '{str(region)}' with tags: {dict_tags}"
            ) from error_instance

    def dispose_certificate(self, certificate):
        """
        Standard.

        :param certificate:
        :return:
        """

        current_certificate = self.get_certificate_by_tags(certificate.region,
                                                           {tag["Key"]: tag["Value"] for tag in certificate.tags},
                                                           ignore_missing_tag=True)
        if not current_certificate:
            raise RuntimeError("Was not able to find certificate")

        logger.info(
            f"Disposing certificate. Domain Name: {current_certificate.domain_name} ARN: {current_certificate.arn}")

        for response in self.execute(self.get_session_client(region=certificate.region).delete_certificate, None,
                                     raw_data=True,
                                     filters_req={"CertificateArn": current_certificate.arn}):
            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                logger.error(response)
                return False

        self.clear_cache(certificate.__class__)
        return True

    def import_certificate_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """
        logger.info(f"Importing certificate: {request_dict['CertificateArn']}")
        for response in self.execute(
                self.get_session_client(region=region).import_certificate, "CertificateArn", filters_req=request_dict
        ):
            return response
