"""
Kafka API

"""

import sys
from kafka import KafkaProducer

from horey.h_logger import get_logger

logger = get_logger()


class KafkaAPI:
    """
    API to work with Grafana 8 API
    """

    def produce(self, server_address):
        """
        Produce message.

        :param server_address:
        :return:
        """

        producer: KafkaProducer = KafkaProducer(bootstrap_servers=server_address)
        future = producer.send("quickstart", b"another_message")
        print(future)
        print(future.get(timeout=10))
        producer.flush()


KafkaAPI().produce(sys.argv[1])
