"""
Test AWS client.

"""
import datetime

import pytest

# pylint: disable=missing-function-docstring

from horey.aws_api.aws_clients.wafv2_client import WAFV2Client
from horey.aws_api.aws_services_entities.wafv2_ip_set import WAFV2IPSet
from horey.aws_api.base_entities.region import Region
from horey.h_logger import get_logger

logger = get_logger()


@pytest.fixture(name="wafv2_client")
def fixture_wafv2_client(main_cache_dir_path):
    client = WAFV2Client()
    client.main_cache_dir_path = main_cache_dir_path
    return client


@pytest.fixture(name="ip_set_src")
def fixture_ip_set_src():
    ip_set = WAFV2IPSet({"Name": "test_cicd",
                         "Scope": "CLOUDFRONT",
                         "Description": "Testing waf ip set cicd",
                         "IPAddressVersion": "IPV4",
                         "Addresses": ["10.0.0.0/32"]})
    ip_set.region = Region.get_region("us-east-1")
    ip_set.tags = [{"Key": "Name", "Value": ip_set.name}]
    return ip_set


@pytest.mark.done
def test_init_wafv2_client(wafv2_client):
    assert isinstance(wafv2_client, WAFV2Client)


@pytest.mark.done
def test_provision_and_dispose_ip_set_raw(wafv2_client, ip_set_src):
    request = ip_set_src.generate_create_request()

    response_create = wafv2_client.provision_ip_set_raw(ip_set_src.region, request)

    ip_set_src.update_from_raw_response(response_create["Summary"])
    request = ip_set_src.generate_dispose_request()

    response_dispose = wafv2_client.dispose_ip_set_raw(ip_set_src.region, request)

    assert response_dispose


@pytest.mark.done
def test_yield_ip_sets_raw(wafv2_client, ip_set_src):
    for x in wafv2_client.yield_ip_sets_raw(ip_set_src.region):
        assert x


@pytest.mark.done
def test_yield_ip_sets_cloudfront_raw(wafv2_client, ip_set_src: WAFV2IPSet):
    for x in wafv2_client.yield_ip_sets_raw(ip_set_src.region, filters_req={"Scope": ip_set_src.scope}):
        assert x


@pytest.mark.done
def test_yield_ip_sets(wafv2_client, ip_set_src):
    for x in wafv2_client.yield_ip_sets(ip_set_src.region):
        assert x


@pytest.mark.done
def test_yield_ip_sets_cloudfront(wafv2_client, ip_set_src: WAFV2IPSet):
    for x in wafv2_client.yield_ip_sets(ip_set_src.region, filters_req={"Scope": ip_set_src.scope}):
        assert x


@pytest.mark.done
def test_provision_ip_set_raw(wafv2_client, ip_set_src):
    request = ip_set_src.generate_create_request()
    response_create = wafv2_client.provision_ip_set_raw(ip_set_src.region, request)
    assert response_create


@pytest.mark.done
def test_update_ip_set_information(wafv2_client, ip_set_src: WAFV2IPSet):
    assert wafv2_client.update_ip_set_information(ip_set_src)


@pytest.mark.done
def test_update_ip_set_information_with_id(wafv2_client, ip_set_src: WAFV2IPSet):
    wafv2_client.update_ip_set_information(ip_set_src)
    assert ip_set_src.name
    assert ip_set_src.id
    assert wafv2_client.update_ip_set_information(ip_set_src)


@pytest.mark.wip
def test_provision_ip_set(wafv2_client, ip_set_src):
    assert wafv2_client.provision_ip_set(ip_set_src)


@pytest.mark.wip
def test_update_ip_set_raw(wafv2_client, ip_set_src):
    ip_set_current = WAFV2IPSet({"Name": ip_set_src.name, "Scope": ip_set_src.scope})
    ip_set_current.region = ip_set_src.region
    wafv2_client.update_ip_set_information(ip_set_current)

    ip_set_src.addresses = ["192.168.0.0/16"]
    ip_set_src.description = "Testing cicd Changed description"
    ip_set_src.lock_token = ip_set_current.lock_token
    ip_set_src.id = ip_set_current.id

    request = ip_set_current.generate_update_request(ip_set_src)
    response = wafv2_client.update_ip_set_raw(ip_set_src.region, request)
    assert response.get("NextLockToken")
    wafv2_client.update_ip_set_information(ip_set_current)
    assert ip_set_current.lock_token == response.get("NextLockToken")
    assert ip_set_current.description == ip_set_src.description
    assert ip_set_current.addresses == ip_set_src.addresses


@pytest.mark.todo
def test_dispose_ip_set(wafv2_client, ip_set_src):
    assert wafv2_client.dispose_ip_set(ip_set_src)
