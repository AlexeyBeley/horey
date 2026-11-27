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
        self._client = None

    @property
    def client(self) -> redis.Redis:
        """
        Connect client
        :return:
        """

        if not self._client:
            self._client = redis.Redis(host=self.configuration.host, port=self.configuration.port, db=0, protocol=3, ssl=True,
                                       ssl_cert_reqs=None,
                                       ssl_check_hostname=False
                                       )

        return self._client

    def write_stream(self, stream_name, data):
        """
        Execute get call
        @param request_path:
        @param data:
        @return:
        """

        return self.client.xadd(stream_name, data)
        #self.client.set("key", "value")

    def read_stream(self, stream_name, count=None):
        """
        Read from stream

        :param stream_name:
        :param count:
        :return:
        """

        ret = []
        messages = self.client.xread({stream_name: '0'}, count=count)
        for stream, msgs in messages.items():
            if len(msgs) != 1:
                raise ValueError(msgs)
            for msg_id, fields in msgs[0]:
                ret.append((msg_id, fields))

        self.client.xdel(stream_name, *[msg_id for msg_id, _ in ret])
        return ret