"""
Opensearch API
https://opensearch.org/docs/2.12/api-reference/

"""

import redis
from horey.h_logger import get_logger
from horey.redis_api.redis_api_configuration_policy import (
    RedisAPIConfigurationPolicy,
)


logger = get_logger()


class RedisAPI:
    """
    API to work with Opensearch 8 API
    """

    def __init__(self, configuration: RedisAPIConfigurationPolicy = None):
        self._monitors = None
        self.configuration = configuration

    def create_stream(self, stream_name):
        """
        Execute get call
        @param request_path:
        @param data:
        @return:
        """

        breakpoint()
