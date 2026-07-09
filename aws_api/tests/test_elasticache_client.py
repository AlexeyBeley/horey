"""
Elasticache cluster.

"""

import os
import pytest
from six import assertRegex

from horey.aws_api.aws_clients.elasticache_client import ElasticacheClient
from horey.aws_api.aws_services_entities.elasticache_replication_group import (
    ElasticacheReplicationGroup,
)
from horey.aws_api.aws_services_entities.elasticache_cache_subnet_group import (
    ElasticacheCacheSubnetGroup,
)
from horey.aws_api.aws_services_entities.elasticache_user import ElasticacheUser
from horey.aws_api.aws_services_entities.elasticache_user_group import ElasticacheUserGroup

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region


ElasticacheClient().main_cache_dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..",
            "ignore",
            "cache"
        )
    )

# pylint: disable= missing-function-docstring

@pytest.mark.todo
def test_init_client():
    assert isinstance(ElasticacheClient(), ElasticacheClient)


@pytest.mark.done
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

@pytest.mark.done
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


@pytest.mark.todo
def test_get_all_clusters():
    client = ElasticacheClient()
    ret = client.get_all_clusters()
    assert len(ret) > 0

@pytest.mark.todo
def test_yield_clusters():
    client = ElasticacheClient()
    obj = None
    for obj in client.yield_clusters():
        break
    assert obj.arn is not None


@pytest.mark.unit
def test_yield_user_groups():
    client = ElasticacheClient()
    obj = None
    for obj in client.yield_user_groups(region=Region.get_region("us-west-2")):
        break
    assert obj.arn is not None

@pytest.mark.unit
def test_yield_users():
    client = ElasticacheClient()
    obj = None
    for obj in client.yield_users(region=Region.get_region("us-west-2")):
        break
    assert obj.arn is not None

@pytest.mark.unit
def test_update_user_information():
    client = ElasticacheClient()
    region = Region.get_region("us-west-2")
    user = ElasticacheUser({})
    user.region = region
    user.id = "default"
    user.user_name = "default"
    user.engine = "redis"
    assert client.update_user_information(user)


@pytest.mark.unit
def test_provision_user():
    client = ElasticacheClient()
    region = Region.get_region("us-west-2")
    user = ElasticacheUser({})
    user.region = region
    user.id = "test"
    user.user_name = "test"
    user.engine = "redis"
    user.passwords = ["Qwerty1234567891011!", "Aa1234567891011!"]
    user.access_string = "on ~* +@all"
    user.tags = [
        {"Key": "lvl", "Value": "tst"},
        {"Key": "name", "Value": user.id},
    ]
    client.provision_user(user)
    assert user.arn is not None
    assert client.update_user_information(user)


@pytest.mark.unit
def test_dispose_user():
    client = ElasticacheClient()
    region = Region.get_region("us-west-2")
    user = ElasticacheUser({})
    user.region = region
    user.id = "test"
    user.user_name = "test"
    user.engine = "redis"
    assert client.dispose_user(user)
    assert not client.update_user_information(user)


@pytest.mark.unit
def test_update_user_group_information():
    client = ElasticacheClient()
    region = Region.get_region("us-west-2")
    for obj in client.yield_user_groups(region=region):
        assert client.update_user_group_information(obj)


@pytest.mark.wip
def test_provision_user_group():
    client = ElasticacheClient()
    region = Region.get_region("us-west-2")
    user_group = ElasticacheUserGroup({})
    user_group.region = region
    user_group.id = "test"
    user_group.engine = "redis"
    user_group.tags = [
        {"Key": "lvl", "Value": "tst"},
        {"Key": "name", "Value": user_group.id},
    ]
    for user in client.yield_users(region=region):
        if user.user_name == "default":
            user_group.user_ids = [user.id]
            break
    else:
        raise RuntimeError("Was not able to find 'default' user")


    client.provision_user_group(user_group)
    assert user_group.arn is not None
    assert client.update_user_group_information(user_group)


@pytest.mark.wip
def test_dispose_user_group():
    client = ElasticacheClient()
    region = Region.get_region("us-west-2")
    user_group = ElasticacheUserGroup({})
    user_group.region = region
    user_group.id = "test"
    assert client.dispose_user_group(user_group)
    assert not client.update_user_group_information(user_group)

