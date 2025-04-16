"""
Test RDS client
"""
import os

import pytest

from horey.aws_api.aws_clients.rds_client import RDSClient
from horey.aws_api.aws_services_entities.rds_db_cluster import RDSDBCluster
from horey.aws_api.aws_services_entities.rds_db_instance import RDSDBInstance
from horey.aws_api.aws_services_entities.rds_db_subnet_group import RDSDBSubnetGroup
from horey.aws_api.aws_services_entities.rds_db_cluster_parameter_group import (
    RDSDBClusterParameterGroup,
)
from horey.aws_api.aws_services_entities.rds_db_cluster_snapshot import (
    RDSDBClusterSnapshot,
)
from horey.aws_api.aws_services_entities.rds_db_parameter_group import (
    RDSDBParameterGroup,
)

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.common_utils.common_utils import CommonUtils


mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


RDSClient().main_cache_dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..",
            "ignore",
            "cache"
        )
    )

# pylint: disable= missing-function-docstring

@pytest.mark.todo
def test_init_rds_client():
    assert isinstance(RDSClient(), RDSClient)


@pytest.mark.todo
def test_clear_cache():
    client = RDSClient()
    client.clear_cache(RDSDBCluster)


@pytest.mark.skip
def test_provision_cluster():
    client = RDSClient()
    cluster = RDSDBCluster({})
    cluster.region = AWSAccount.get_aws_region()

    cluster.db_subnet_group_name = "db_subnet-test"
    cluster.db_cluster_parameter_group_name = "cluster-param-group-test"
    cluster.backup_retention_period = 35
    cluster.database_name = "db_test"
    cluster.db_cluster_identifier = "cluster-db-test"
    cluster.vpc_security_group_ids = ["sg-11111111111"]
    cluster.engine = "aurora-mysql"
    cluster.engine_version = "5.7.mysql_aurora.2.09.2"
    cluster.port = 3306

    cluster.master_username = "admin"
    cluster.master_user_password = "12345678"
    cluster.preferred_backup_window = "09:23-09:53"
    cluster.preferred_maintenance_window = "sun:03:30-sun:04:00"
    cluster.storage_encrypted = True
    # cluster.kms_key_id = True
    cluster.engine_mode = "provisioned"

    cluster.deletion_protection = False
    cluster.copy_tags_to_snapshot = True
    cluster.enable_cloudwatch_logs_exports = ["audit", "error", "general", "slowquery"]

    cluster.tags = [
        {"Key": "lvl", "Value": "tst"},
        {"Key": "name", "Value": cluster.db_cluster_identifier},
    ]

    client.provision_db_cluster(cluster)

    assert cluster.arn is not None

@pytest.mark.skip
def test_provision_cluster_from_snapshot():
    client = RDSClient()
    cluster = RDSDBCluster({})
    cluster.region = AWSAccount.get_aws_region()

    cluster.db_subnet_group_name = "db_subnet-test"
    cluster.db_cluster_parameter_group_name = "cluster-param-group-test"
    cluster.backup_retention_period = 35
    cluster.database_name = "db_test"
    cluster.id = "cluster-db-test"
    cluster.vpc_security_group_ids = [mock_values["cluster.vpc_security_group_ids"]]
    cluster.engine = "aurora-mysql"
    cluster.engine_version = "5.7.mysql_aurora.2.09.2"
    cluster.port = 3306

    cluster.master_username = "admin"
    cluster.master_user_password = "12345678"
    cluster.preferred_backup_window = "09:23-09:53"
    cluster.preferred_maintenance_window = "sun:03:30-sun:04:00"
    cluster.storage_encrypted = True
    # cluster.kms_key_id = True
    cluster.engine_mode = "provisioned"

    cluster.deletion_protection = False
    cluster.copy_tags_to_snapshot = True
    cluster.enable_cloudwatch_logs_exports = ["audit", "error", "general", "slowquery"]

    cluster.tags = [
        {"Key": "lvl", "Value": "tst"},
        {"Key": "name", "Value": cluster.id},
    ]

    client.provision_db_cluster(cluster, snapshot_id="horey-test-snapshot-id")

    assert cluster.arn is not None

@pytest.mark.skip
def test_dispose_db_cluster():
    client = RDSClient()
    cluster = RDSDBCluster({})
    cluster.region = AWSAccount.get_aws_region()

    cluster.skip_final_snapshot = True
    cluster.id = "cluster-db-test"

    client.dispose_db_cluster(cluster)

@pytest.mark.skip
def test_provision_db_instance():
    client = RDSClient()
    db_instance = RDSDBInstance({})
    db_instance.region = AWSAccount.get_aws_region()

    db_instance.id = "instance-db-test-1"
    db_instance.db_instance_class = "db.t3.medium"
    db_instance.db_cluster_identifier = "cluster-db-test"
    db_instance.db_subnet_group_name = "db_subnet-test"
    db_instance.db_parameter_group_name = "param-group-test"
    db_instance.engine = "aurora-mysql"
    db_instance.engine_version = "5.7.mysql_aurora.2.09.2"

    db_instance.preferred_maintenance_window = "sun:03:30-sun:04:00"
    db_instance.storage_encrypted = True

    db_instance.copy_tags_to_snapshot = True

    db_instance.tags = [
        {"Key": "lvl", "Value": "tst"},
        {"Key": "name", "Value": db_instance.id},
    ]

    client.provision_db_instance(db_instance)

    assert db_instance.arn is not None

@pytest.mark.skip
def test_provision_subnet_group():
    client = RDSClient()
    subnet_group = RDSDBSubnetGroup({})
    subnet_group.region = AWSAccount.get_aws_region()
    subnet_group.name = "db_subnet-test"
    subnet_group.db_subnet_group_description = "db subnet test"
    subnet_group.subnet_ids = ["subnet-yy", "subnet-xx"]
    subnet_group.tags = [
        {"Key": "lvl", "Value": "tst"},
        {"Key": "name", "Value": subnet_group.name},
    ]
    client.provision_db_subnet_group(subnet_group)

    assert subnet_group.arn is not None

@pytest.mark.skip
def test_provision_db_parameter_group():
    client = RDSClient()
    db_parameter_group = RDSDBParameterGroup({})
    db_parameter_group.region = AWSAccount.get_aws_region()
    db_parameter_group.name = "param-group-test"
    db_parameter_group.db_parameter_group_family = "aurora-mysql5.7"
    db_parameter_group.description = "test"
    db_parameter_group.tags = [
        {"Key": "lvl", "Value": "tst"},
        {"Key": "name", "Value": db_parameter_group.name},
    ]
    client.provision_db_parameter_group(db_parameter_group)

    assert db_parameter_group.arn is not None

@pytest.mark.skip
def test_provision_db_cluster_parameter_group():
    client = RDSClient()
    db_cluster_parameter_group = RDSDBClusterParameterGroup({})
    db_cluster_parameter_group.region = AWSAccount.get_aws_region()
    db_cluster_parameter_group.name = "cluster-param-group-test"
    db_cluster_parameter_group.db_parameter_group_family = "aurora-mysql5.7"
    db_cluster_parameter_group.description = "test"
    db_cluster_parameter_group.tags = [
        {"Key": "lvl", "Value": "tst"},
        {"Key": "name", "Value": db_cluster_parameter_group.name},
    ]
    client.provision_db_cluster_parameter_group(db_cluster_parameter_group)

    assert db_cluster_parameter_group.arn is not None

@pytest.mark.skip
def test_copy_db_cluster_snapshot():
    client = RDSClient()
    snapshot_src = RDSDBClusterSnapshot({})
    snapshot_src.region = Region.get_region("us-east-1")
    snapshot_src.db_cluster_identifier = mock_values[
        "snapshot_src.db_cluster_identifier"
    ]

    snapshot_dst = RDSDBClusterSnapshot({})
    snapshot_dst.region = Region.get_region("us-west-2")
    snapshot_dst.id = "horey-test-snapshot-id"
    snapshot_dst.tags = [
        {"Key": "lvl", "Value": "tst"},
        {"Key": "name", "Value": snapshot_dst.id},
    ]
    client.copy_db_cluster_snapshot(snapshot_src, snapshot_dst)


@pytest.mark.todo
def test_get_default_engine_version():
    client = RDSClient()
    assert client.get_default_engine_version(Region.get_region("us-west-2"), "aurora-mysql") is not None
    # from_cache
    assert client.get_default_engine_version(Region.get_region("us-west-2"), "aurora-mysql") is not None

@pytest.mark.todo
def test_yield_db_clusters():
    client = RDSClient()
    cluster = None
    for cluster in client.yield_db_clusters(Region.get_region("us-west-2")):
        break
    assert cluster.arn is not None

@pytest.mark.todo
def test_get_all_db_clusters_no_region_no_full_information_tags_false():
    client = RDSClient()
    file_path = client.generate_cache_file_path(RDSDBCluster, "us-west-2", full_information=False, get_tags=False)
    assert client.get_all_db_clusters(region=None, full_information=False, get_tags=False)
    assert os.path.exists(file_path)


@pytest.mark.todo
def test_get_all_db_clusters_region_full_information_tags_true():
    client = RDSClient()
    file_path = client.generate_cache_file_path(RDSDBCluster, "us-west-2", full_information=True, get_tags=True)
    assert client.get_all_db_clusters(region=Region.get_region("us-west-2"), full_information=True, get_tags=True)
    assert os.path.exists(file_path)


@pytest.mark.todo
def test_get_region_db_clusters():
    client = RDSClient()
    assert client.get_region_db_clusters(Region.get_region("us-west-2"))


@pytest.mark.todo
def test_get_region_db_subnet_groups():
    client = RDSClient()
    ret = client.get_region_db_subnet_groups(Region.get_region("us-west-2"))
    assert len(ret) > 0

@pytest.mark.todo
def test_yield_db_subnet_groups():
    client = RDSClient()
    obj = None
    for obj in client.yield_db_subnet_groups():
        break
    assert obj.arn is not None

@pytest.mark.todo
def test_get_region_db_cluster_parameter_groups():
    client = RDSClient()
    ret = client.get_region_db_cluster_parameter_groups(Region.get_region("us-west-2"))
    assert len(ret) > 0

@pytest.mark.todo
def test_get_region_db_cluster_parameter_groups_full_info_false():
    client = RDSClient()
    ret = client.get_region_db_cluster_parameter_groups(Region.get_region("us-west-2"), full_information=False)
    assert len(ret) > 0


@pytest.mark.todo
def test_yield_db_cluster_parameter_groups():
    client = RDSClient()
    obj = None
    for obj in client.yield_db_cluster_parameter_groups():
        break
    assert obj.arn is not None

@pytest.mark.todo
def test_get_region_db_instances_update_tags_true():
    client = RDSClient()
    ret = client.get_region_db_instances(Region.get_region("us-west-2"), update_tags=True)
    assert len(ret) > 0

@pytest.mark.todo
def test_get_region_db_instances_update_tags_false():
    client = RDSClient()
    ret = client.get_region_db_instances(Region.get_region("us-west-2"), update_tags=False)
    assert len(ret) > 0


@pytest.mark.todo
def test_yield_db_instances():
    client = RDSClient()
    obj = None
    for obj in client.yield_db_instances():
        break
    assert obj.arn is not None

@pytest.mark.todo
def test_yield_db_cluster_snapshots():
    client = RDSClient()
    obj = None
    for obj in client.yield_db_cluster_snapshots():
        break
    assert obj.arn is not None


def test_yield_db_cluster_snapshots_full_information_false_get_tags_false():
    client = RDSClient()
    obj = None
    for obj in client.yield_db_cluster_snapshots(full_information=False, get_tags=False):
        break
    assert obj.arn is not None

def test_get_all_db_cluster_snapshots():
    client = RDSClient()
    ret = client.get_all_db_cluster_snapshots()
    assert len(ret) > 0


def test_get_region_db_cluster_snapshots():
    client = RDSClient()
    ret = client.get_region_db_cluster_snapshots(Region.get_region("us-west-2"))
    assert len(ret) > 0
