"""
ELB V2 client tests.

"""
import os
import pytest

from horey.aws_api.aws_clients.elb_client import ELBClient
from horey.common_utils.common_utils import CommonUtils


ELBClient().main_cache_dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..",
            "ignore",
            "cache"
        )
    )

client = ELBClient()

# pylint: disable= missing-function-docstring

@pytest.mark.todo
def test_init_client():
    assert isinstance(ELBClient(), ELBClient)

@pytest.mark.todo
def test_get_all_load_balancers():
    response = client.get_all_load_balancers()
    assert len(response) > 1

@pytest.mark.todo
def test_yield_load_balancers():
    obj = None
    for obj in client.yield_load_balancers():
        break
    assert obj.arn is not None
