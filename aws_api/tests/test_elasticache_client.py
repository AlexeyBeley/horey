import os
import pdb
import sys

from horey.aws_api.aws_clients.elasticache_client import ElasticacheClient
from horey.aws_api.aws_services_entities.elasticache_replication_group import (
    ElasticacheReplicationGroup,
)
from horey.aws_api.aws_services_entities.elasticache_cache_subnet_group import (
    ElasticacheCacheSubnetGroup,
)

from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.common_utils.common_utils import CommonUtils


configuration_values_file_full_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py"
)
logger = get_logger(
    configuration_values_file_full_path=configuration_values_file_full_path
)

accounts_file_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "ignore",
        "aws_api_managed_accounts.py",
    )
)

accounts = CommonUtils.load_object_from_module(accounts_file_full_path, "main")
AWSAccount.set_aws_account(accounts["1111"])
AWSAccount.set_aws_region(accounts["1111"].regions["us-west-2"])

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


def test_init_client():
    assert isinstance(ElasticacheClient(), ElasticacheClient)


def test_provision_replication_group():
    client = ElasticacheClient()
    replication_group = ElasticacheReplicationGroup({})
    replication_group.region = AWSAccount.get_aws_region()

    replication_group.id = "horey-test-redis"
    replication_group.az_mode = "cross-az"
    replication_group.description = "horey-test-redis replication group"
    replication_group.preferred_cache_cluster_azs = mock_values[
        "elasticache.replication_group.preferred_cache_cluster_azs"
    ]
    replication_group.num_cache_clusters = 2
    replication_group.cache_node_type = "cache.t3.micro"
    replication_group.engine = "redis"
    replication_group.engine_version = "6.x"
    # replication_group.security_group_ids = [redis_security_group.id]
    replication_group.cache_parameter_group_name = "default.redis6.x"
    replication_group.cache_subnet_group_name = "subnet-group-horey-test"

    replication_group.preferred_maintenance_window = "sat:01:30-sat:02:30"
    replication_group.auto_minor_version_upgrade = True
    replication_group.snapshot_retention_limit = 2
    replication_group.snapshot_window = "02:31-03:32"

    replication_group.tags = [
        {"Key": "lvl", "Value": "tst"},
        {"Key": "name", "Value": replication_group.id},
    ]

    client.provision_replication_group(replication_group)

    assert replication_group.arn is not None


def test_provision_subnet_group():
    client = ElasticacheClient()
    subnet_group = ElasticacheCacheSubnetGroup({})
    subnet_group.region = AWSAccount.get_aws_region()
    subnet_group.name = "subnet-group-horey-test"
    subnet_group.cache_subnet_group_description = "db subnet test"
    subnet_group.subnet_ids = mock_values["elasticache.subnet_group.subnet_ids"]
    subnet_group.tags = [
        {"Key": "lvl", "Value": "tst"},
        {"Key": "name", "Value": subnet_group.name},
    ]
    client.provision_subnet_group(subnet_group)
    assert subnet_group.arn is not None


if __name__ == "__main__":
    test_init_client()
    # test_provision_subnet_group()
    test_provision_replication_group()
