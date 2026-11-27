"""
Test route 53 client.

"""

import os
import pytest

from horey.aws_api.aws_clients.route53_client import Route53Client

# pylint: disable= missing-function-docstring

Route53Client().main_cache_dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..",
            "ignore",
            "cache"
        )
    )

@pytest.mark.todo
def test_init_route53_client():
    assert isinstance(Route53Client(), Route53Client)

@pytest.mark.todo
def test_yield_hosted_zones():
    client = Route53Client()
    obj = None
    for obj in client.yield_hosted_zones():
        break
    assert obj.id is not None


@pytest.mark.todo
def test_get_all_hosted_zones_full_info_true():
    client = Route53Client()
    ret = client.get_all_hosted_zones(full_information=True)
    assert len(ret) > 0


@pytest.mark.todo
def test_get_all_hosted_zones_full_info_false():
    client = Route53Client()
    ret = client.get_all_hosted_zones(full_information=False)
    assert len(ret) > 0
