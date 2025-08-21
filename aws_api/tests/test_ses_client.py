"""
Test SES client.

"""

import os
import pytest

# pylint: disable=missing-function-docstring

from horey.aws_api.aws_clients.ses_client import SESClient
from horey.aws_api.aws_services_entities.ses_receipt_rule_set import SESReceiptRuleSet
from horey.aws_api.base_entities.region import Region

SESClient().main_cache_dir_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "..",
        "ignore",
        "cache"
    )
)

client = SESClient()

RULE_SET_NAME = "rest_rule_set"


@pytest.fixture(name="base_rule_set")
def fixture_base_rule_set():
    rule_set = SESReceiptRuleSet({})
    rule_set.region = Region.get_region("us-west-2")
    rule_set.name = RULE_SET_NAME
    rule_set.tags = [{
        "Key": "Name",
        "Value": RULE_SET_NAME
    }]
    return rule_set


@pytest.mark.done
def test_init_ses_client():
    assert isinstance(SESClient(), SESClient)


@pytest.mark.done
def test_yield_identities():
    obj = None
    for obj in client.yield_identities():
        break
    assert obj.name is not None


@pytest.mark.done
def test_yield_receipt_rule_sets():
    objs = list(client.yield_receipt_rule_sets())
    assert objs[0].rules is not None


@pytest.mark.done
def test_update_rule_set_information(base_rule_set):
    assert not client.update_rule_set_information(base_rule_set)


@pytest.mark.done
def test_generate_change_rules_requests_create(base_rule_set):
    desired = SESReceiptRuleSet({"name": base_rule_set.name})
    desired.rules = [{"Name": "string", "Enabled": False}]
    reorder, create, delete = base_rule_set.generate_change_rules_requests(desired)
    assert create
    assert not reorder
    assert not delete


@pytest.mark.done
def test_generate_change_rules_requests_delete(base_rule_set):
    base_rule_set.rules = [{"Name": "string", "Enabled": False}]
    desired = SESReceiptRuleSet({"name": base_rule_set.name})
    reorder, create, delete = base_rule_set.generate_change_rules_requests(desired)
    assert not create
    assert not reorder
    assert delete


@pytest.mark.done
def test_generate_change_rules_requests_reoder(base_rule_set):
    base_rule_set.rules = [{"Name": "string2", "Enabled": False}, {"Name": "string1", "Enabled": False} ]
    desired = SESReceiptRuleSet({"name": base_rule_set.name})
    desired.rules = [{"Name": "string1", "Enabled": False}, {"Name": "string2", "Enabled": False}]
    reorder, create, delete = base_rule_set.generate_change_rules_requests(desired)
    assert not create
    assert reorder
    assert not delete


@pytest.mark.done
def test_generate_change_rules_requests_reorder_create_delete(base_rule_set):
    base_rule_set.rules = [{"Name": "string2", "Enabled": False}, {"Name": "string1", "Enabled": False}, {"Name": "string0", "Enabled": False}]
    desired = SESReceiptRuleSet({"name": base_rule_set.name})
    desired.rules = [{"Name": "string1", "Enabled": False}, {"Name": "string2", "Enabled": False}, {"Name": "string3", "Enabled": False}]
    reorder, create, delete = base_rule_set.generate_change_rules_requests(desired)
    assert create
    assert reorder
    assert delete


@pytest.mark.done
def test_generate_update_receipt_rule_requests(base_rule_set):
    base_rule_set.rules = [{"Name": "string2", "Enabled": True}, {"Name": "string1", "Enabled": True}, {"Name": "string0", "Enabled": False}]
    desired = SESReceiptRuleSet({"name": base_rule_set.name})
    desired.rules = [{"Name": "string1", "Enabled": False}, {"Name": "string2", "Enabled": False}, {"Name": "string3", "Enabled": False}]
    requests = base_rule_set.generate_update_receipt_rule_requests(desired)
    assert requests == [{"RuleSetName": "rest_rule_set", "Rule": {"Name": "string2", "Enabled": False}}, {"RuleSetName": "rest_rule_set", "Rule": {"Name": "string1", "Enabled": False}}]


@pytest.mark.done
def test_provision_receipt_rule_set(base_rule_set):
    client.provision_receipt_rule_set(base_rule_set)
    assert base_rule_set.created_timestamp is not None


@pytest.mark.todo
def test_get_active_rule_set_name(base_rule_set):
    assert client.get_active_rule_set_name(base_rule_set.region)
