"""
Test SES V2 client.

"""

import os
import pytest

# pylint: disable=missing-function-docstring

from horey.aws_api.aws_clients.sesv2_client import SESV2Client
from horey.aws_api.aws_services_entities.sesv2_email_template import SESV2EmailTemplate
from horey.aws_api.aws_services_entities.sesv2_email_identity import SESV2EmailIdentity
from horey.aws_api.aws_services_entities.sesv2_configuration_set import (
    SESV2ConfigurationSet,
)
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.common_utils.common_utils import CommonUtils

SESV2Client().main_cache_dir_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "..",
        "ignore",
        "cache"
    )
)

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


def test_init_sesv2_client():
    assert isinstance(SESV2Client(), SESV2Client)


@pytest.mark.todo
def test_provision_email_identity():
    client = SESV2Client()
    email_identity = SESV2EmailIdentity({})
    email_identity.name = mock_values["email_identity.name"]
    email_identity.region = Region.get_region("us-west-2")
    email_identity.tags = [{"Key": "name", "Value": "value"}]
    client.provision_email_identity(email_identity)


@pytest.mark.wip
def test_provision_email_template():
    client = SESV2Client()
    email_template = SESV2EmailTemplate({})
    email_template.name = "test"
    email_template.region = Region.get_region("us-west-2")
    email_template.template_content = {"Subject": "test_subject", "Text": "sample text"}
    client.provision_email_template(email_template)


@pytest.mark.wip
def test_provision_email_template_update():
    client = SESV2Client()
    email_template = SESV2EmailTemplate({})
    email_template.name = "test"
    email_template.region = Region.get_region("us-west-2")
    email_template.template_content = {"Subject": "test_subject_change", "Text": "sample text_2"}
    client.provision_email_template(email_template)


@pytest.mark.todo
def test_get_region_suppressed_destinations():
    client = SESV2Client()
    ret = client.get_region_suppressed_destinations(region)
    assert isinstance(ret, list)


@pytest.mark.todo
def test_provision_configuration_set():
    client = SESV2Client()
    configuration_set = SESV2ConfigurationSet({})
    configuration_set.name = "test"
    configuration_set.region = Region.get_region("us-west-2")
    configuration_set.tracking_options = {
        "CustomRedirectDomain": mock_values["email_identity.name"]
    }
    configuration_set.reputation_options = {"ReputationMetricsEnabled": False}
    configuration_set.sending_options = {"SendingEnabled": True}
    configuration_set.tags = [{"Key": "name", "Value": "value"}]
    client.provision_configuration_set(configuration_set)


region = Region.get_region("us-west-2")


@pytest.mark.todo
def test_send_email():
    AWSAccount.set_aws_region("us-west-2")
    client = SESV2Client()
    from_address = mock_values["from_address_private"]
    from_address = mock_values["from_address_domain"]
    to_address = mock_values["to_address"]

    dict_request = {"FromEmailAddress": from_address,
                    "Destination": {"ToAddresses": [to_address, ]},
                    "Content": {'Simple': {"Subject": {
                        "Data": "Hello"},
                        "Body": {
                            "Text": {
                                "Data": "world",
                            }}
                    }},
                    "EmailTags": [
                        {
                            "Name": "Name",
                            "Value": "Horey"
                        },
                    ],
                    }
    client.send_email_raw(region, dict_request)


@pytest.mark.todo
def test_send_email_with_config_set():
    AWSAccount.set_aws_region("us-west-2")
    client = SESV2Client()
    from_address = mock_values["from_address_private"]
    from_address = mock_values["from_address_domain"]
    to_address = mock_values["to_address"]
    to_address = "horey@gmail.com"

    dict_request = {"FromEmailAddress": from_address,
                    "Destination": {"ToAddresses": [to_address, ]},
                    "Content": {'Simple': {"Subject": {
                        "Data": "Hello config set"},
                        "Body": {
                            "Text": {
                                "Data": "world",
                            }}
                    }},
                    "EmailTags": [
                        {
                            "Name": "Name",
                            "Value": "Horey"
                        },
                    ],
                    "ConfigurationSetName": mock_values["ConfigurationSetName"],
                    }
    client.send_email_raw(region, dict_request)


@pytest.mark.todo
def test_send_email_with_config_set_html():
    body_ = """<html><head></head><body><h1>A header 1</h1><br>Some text."""
    AWSAccount.set_aws_region("us-west-2")
    client = SESV2Client()
    from_address = mock_values["from_address_private"]
    from_address = mock_values["from_address_domain2"]
    to_address = mock_values["to_address"]
    to_address = "horey@gmail.com"

    dict_request = {"FromEmailAddress": from_address,
                    "Destination": {"ToAddresses": [to_address, ]},
                    "Content": {'Simple': {"Subject": {
                        "Data": "Hello config set"},
                        "Body": {
                            "Html": {
                                "Data": body_,
                            }}
                    }},
                    "EmailTags": [
                        {
                            "Name": "Name",
                            "Value": "Horey"
                        },
                    ],
                    "ConfigurationSetName": mock_values["ConfigurationSetName2"],
                    }
    client.send_email_raw(region, dict_request)


@pytest.mark.done
def test_yield_configuration_sets():
    client = SESV2Client()
    obj = None
    for obj in client.yield_configuration_sets():
        break
    assert obj.name is not None


@pytest.mark.done
def test_get_all_configuration_sets_full_information_false():
    client = SESV2Client()
    ret = client.get_all_configuration_sets(full_information=False)
    assert len(ret) > 0


@pytest.mark.done
def test_get_all_configuration_sets_full_information_true():
    client = SESV2Client()
    ret = client.get_all_configuration_sets(full_information=True)
    assert len(ret) > 0


@pytest.mark.done
def test_yield_email_templates():
    client = SESV2Client()
    obj = None
    for obj in client.yield_email_templates():
        break
    assert obj.name is not None


@pytest.mark.done
def test_get_all_email_templates_full_information_false():
    client = SESV2Client()
    ret = client.get_all_email_templates(full_information=False)
    assert len(ret) > 0


@pytest.mark.done
def test_get_all_email_templates_full_information_true():
    client = SESV2Client()
    ret = client.get_all_email_templates(full_information=True)
    assert len(ret) > 0


@pytest.mark.done
def test_yield_email_identities():
    client = SESV2Client()
    obj = None
    for obj in client.yield_email_identities():
        break
    assert obj.name is not None


@pytest.mark.done
def test_get_all_email_identities_full_information_false():
    client = SESV2Client()
    ret = client.get_all_email_identities()
    assert len(ret) > 0


@pytest.mark.wip
def test_yield_accounts():
    client = SESV2Client()
    obj = None
    for obj in client.yield_accounts():
        break
    assert obj.dict_src is not None
