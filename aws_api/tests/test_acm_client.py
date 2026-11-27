"""
Testing acm client

"""

import os
import pytest
from horey.aws_api.aws_clients.acm_client import ACMClient
from horey.aws_api.aws_services_entities.acm_certificate import ACMCertificate
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region


ACMClient().main_cache_dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..",
            "ignore",
            "cache"
        )
    )

# pylint: disable= missing-function-docstring

@pytest.mark.todo
def test_clear_cache():
    ACMClient().clear_cache(ACMCertificate)

@pytest.mark.todo
def test_init_acm_client():
    assert isinstance(ACMClient(), ACMClient)


def provision_certificate():
    client = ACMClient()
    cert = ACMCertificate({})
    cert.region = AWSAccount.get_aws_region()

    cert.domain_name = "*.test.comp.com"
    cert.tags = [
        {"Key": "lvl", "Value": "tst"},
        {"Key": "name", "Value": cert.generate_name_tag()},
    ]

    cert.validation_method = "DNS"

    client.provision_certificate(cert)
    return cert

def fetch_certificates_from_cache():
    client = ACMClient()
    region_dir_name = "us-west-2"
    full_information = False
    get_tags = True
    file_path = client.generate_cache_file_path(ACMCertificate, region_dir_name, full_information, get_tags)
    if os.path.exists(file_path):
        return ACMClient.load_objects_from_cache(ACMCertificate, file_path)
    return []


@pytest.mark.todo
def test_get_all_certificates():
    client = ACMClient()
    ret = client.get_all_certificates()

    assert ret is not None
    assert len(ret) > 0


@pytest.mark.todo
def test_provision_certificate():
    cert = provision_certificate()
    assert cert.arn is not None

    certificates = fetch_certificates_from_cache()
    assert len(certificates) == 0

@pytest.mark.todo
def test_get_certificate_by_tags_raises_no_certificate():
    client = ACMClient()
    dict_tags = {"Name": "NoSuchCertificate"}
    with pytest.raises(Exception, match=r".*No certificates found in region.*"):
        client.get_certificate_by_tags(Region.get_region("us-west-2"), dict_tags, ignore_missing_tag=True)

@pytest.mark.todo
def test_get_certificate_by_tags():
    client = ACMClient()
    certificate = provision_certificate()
    dict_tags = {tag["Key"]: tag["Value"] for tag in certificate.tags}
    fetched_certificate = client.get_certificate_by_tags(Region.get_region("us-west-2"), dict_tags, ignore_missing_tag=True)

    assert fetched_certificate is not None
    assert fetched_certificate.arn == certificate.arn

@pytest.mark.todo
def test_get_certificate():
    client = ACMClient()
    certificate = provision_certificate()
    fetched_certificate = client.get_certificate(certificate.arn)

    assert fetched_certificate is not None
    assert fetched_certificate.arn == certificate.arn

@pytest.mark.todo
def test_dispose_certificate():
    cert = provision_certificate()
    client = ACMClient()
    assert client.dispose_certificate(cert)
    certificates = fetch_certificates_from_cache()
    assert len(certificates) == 0
