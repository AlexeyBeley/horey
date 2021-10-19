import os
import pdb
import sys

from horey.aws_api.aws_clients.sqs_client import SQSClient
from horey.aws_api.aws_services_entities.elasticache_replication_group import ElasticacheReplicationGroup
from horey.aws_api.aws_services_entities.elasticache_cache_subnet_group import ElasticacheCacheSubnetGroup

from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.common_utils.common_utils import CommonUtils


configuration_values_file_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py")
logger = get_logger(configuration_values_file_full_path=configuration_values_file_full_path)

accounts_file_full_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "aws_api_managed_accounts.py"))

accounts = CommonUtils.load_object_from_module(accounts_file_full_path, "main")
AWSAccount.set_aws_account(accounts["1111"])
AWSAccount.set_aws_region(accounts["1111"].regions['us-west-2'])

mock_values_file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"))
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


def test_init_client():
    assert isinstance(SQSClient(), SQSClient)

def test_provision_sqs_queue():
    client = SQSClient()
    sqs_queue = ElasticacheCacheSubnetGroup({})
    sqs_queue.region = AWSAccount.get_aws_region()
    sqs_queue.name = "subnet-group-horey-test"
    sqs_queue.cache_sqs_queue_description = "db subnet test"
    sqs_queue.subnet_ids = mock_values["elasticache.sqs_queue.subnet_ids"]
    sqs_queue.tags = [
        {
            'Key': 'lvl',
            'Value': "tst"
        }, {
            'Key': 'name',
            'Value': sqs_queue.name
        }
    ]
    client.provision_sqs_queue(sqs_queue)
    assert sqs_queue.arn is not None


if __name__ == "__main__":
    test_init_client()
    #test_provision_subnet_group()

