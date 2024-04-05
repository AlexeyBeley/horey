"""
Test SES client.

"""

import os
import pytest

# pylint: disable=missing-function-docstring

from horey.aws_api.aws_clients.ses_client import SESClient

SESClient().main_cache_dir_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "..",
        "ignore",
        "cache"
    )
)

client = SESClient()


@pytest.mark.wip
def test_init_ses_client():
    assert isinstance(SESClient(), SESClient)


@pytest.mark.wip
def test_yield_identities():
    obj = None
    for obj in client.yield_identities():
        break
    assert obj.name is not None


@pytest.mark.wip
def test_yield_receipt_rule_sets():
    objs = list(client.yield_receipt_rule_sets())
    assert objs[0].rules is not None
