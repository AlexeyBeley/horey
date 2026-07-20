"""
Testing opensearch API
"""

import os

import pytest

from horey.redis_api.redis_api import RedisAPI
from horey.redis_api.redis_api_configuration_policy import (
    RedisAPIConfigurationPolicy,
)

ignore_dir_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore"
)

# pylint: disable= missing-function-docstring


@pytest.fixture(name="redis_api")
def fixture_redis_api():
    configuration = RedisAPIConfigurationPolicy()
    configuration.configuration_file_full_path = os.path.abspath(
        os.path.join(ignore_dir_path, "test_redis.py")
    )
    configuration.init_from_file()

    yield RedisAPI(configuration=configuration)



@pytest.mark.unit
def test_write_stream(redis_api):
    assert redis_api.write_stream("test", {'field1': 'value1', 'field2': 'value2'})

@pytest.mark.unit
def test_read_stream(redis_api):
    msgs = redis_api.read_stream("test")
    assert len(msgs)

