"""
Test AWS client.

"""

import pytest

# pylint: disable=missing-function-docstring

from horey.aws_api.aws_clients.s3control_client import S3ControlClient
from horey.h_logger import get_logger
from horey.aws_api.base_entities.region import Region

logger = get_logger()


@pytest.fixture(name="client")
def fixture_client(main_cache_dir_path):
    client = S3ControlClient()
    client.main_cache_dir_path = main_cache_dir_path
    return client


@pytest.mark.done
def test_init_client(client):
    assert isinstance(client, S3ControlClient)


@pytest.mark.done
def test_init_client(client):
    for str_region in ["us-east-1", "eu-central-1"]:
        region = Region.get_region(str_region)
        ret = list(client.yield_access_points(region=region))
    assert ret


