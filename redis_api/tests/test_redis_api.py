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
        os.path.join(ignore_dir_path, "redis", "test_redis.py")
    )
    configuration.init_from_file()

    yield RedisAPI(configuration=configuration)




@pytest.mark.done
def test_create_stream(redis_api):
    assert redis_api.create_stream("test")

