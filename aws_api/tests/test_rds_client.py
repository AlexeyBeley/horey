import os
import sys

from horey.aws_api.aws_clients.rds_client import RDSClient
from horey.aws_api.aws_services_entities.rds_db_cluster import RDSDBCluster
from horey.aws_api.aws_services_entities.rds_db_instance import RDSDBInstance
from horey.aws_api.aws_services_entities.rds_db_subnet_group import RDSDBSubnetGroup
from horey.aws_api.aws_services_entities.rds_db_cluster_parameter_group import RDSDBClusterParameterGroup
from horey.aws_api.aws_services_entities.rds_db_parameter_group import RDSDBParameterGroup

from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region
from horey.common_utils.common_utils import CommonUtils

from unittest.mock import Mock
configuration_values_file_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py")
logger = get_logger(configuration_values_file_full_path=configuration_values_file_full_path)

accounts_file_full_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "aws_api_managed_accounts.py"))

accounts = CommonUtils.load_object_from_module(accounts_file_full_path, "main")
AWSAccount.set_aws_account(accounts["1111"])
AWSAccount.set_aws_region(accounts["1111"].regions['us-west-2'])

mock_values_file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"))
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


def test_init_rds_client():
    assert isinstance(RDSClient(), RDSClient)


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
    #cluster.kms_key_id = True
    cluster.engine_mode = "provisioned"

    cluster.deletion_protection = False
    cluster.copy_tags_to_snapshot = True
    cluster.enable_cloudwatch_logs_exports = [
        "audit",
        "error",
        "general",
        "slowquery"
    ]

    cluster.tags = [
        {
            'Key': 'lvl',
            'Value': "tst"
        }, {
            'Key': 'name',
            'Value': cluster.db_cluster_identifier
        }
    ]

    client.provision_db_cluster(cluster)

    assert cluster.arn is not None


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
        {
            'Key': 'lvl',
            'Value': "tst"
        }, {
            'Key': 'name',
            'Value': db_instance.id
        }
    ]

    client.provision_db_instance(db_instance)

    assert db_instance.arn is not None


def test_provision_subnet_group():
    client = RDSClient()
    subnet_group = RDSDBSubnetGroup({})
    subnet_group.region = AWSAccount.get_aws_region()
    subnet_group.name = "db_subnet-test"
    subnet_group.db_subnet_group_description = "db subnet test"
    subnet_group.subnet_ids = ["subnet-yy", "subnet-xx"]
    subnet_group.tags = [
        {
            'Key': 'lvl',
            'Value': "tst"
        }, {
            'Key': 'name',
            'Value': subnet_group.name
        }
    ]
    client.provision_db_subnet_group(subnet_group)

    assert subnet_group.arn is not None


def test_provision_db_parameter_group():
    client = RDSClient()
    db_parameter_group = RDSDBParameterGroup({})
    db_parameter_group.region = AWSAccount.get_aws_region()
    db_parameter_group.name = "param-group-test"
    db_parameter_group.db_parameter_group_family = "aurora-mysql5.7"
    db_parameter_group.description = "test"
    db_parameter_group.tags = [
        {
            'Key': 'lvl',
            'Value': "tst"
        }, {
            'Key': 'name',
            'Value': db_parameter_group.name
        }
    ]
    client.provision_db_parameter_group(db_parameter_group)

    assert db_parameter_group.arn is not None


def test_provision_db_cluster_parameter_group():
    client = RDSClient()
    db_cluster_parameter_group = RDSDBClusterParameterGroup({})
    db_cluster_parameter_group.region = AWSAccount.get_aws_region()
    db_cluster_parameter_group.name = "cluster-param-group-test"
    db_cluster_parameter_group.db_parameter_group_family = "aurora-mysql5.7"
    db_cluster_parameter_group.description = "test"
    db_cluster_parameter_group.tags = [
        {
            'Key': 'lvl',
            'Value': "tst"
        }, {
            'Key': 'name',
            'Value': db_cluster_parameter_group.name
        }
    ]
    client.provision_db_cluster_parameter_group(db_cluster_parameter_group)

    assert db_cluster_parameter_group.arn is not None


def test_copy_db_snapshot():
    client = RDSClient()
    snapshot_src_mock = Mock()
    snapshot_src_mock.region = Region.get_region("us-east-1")

    snapshot_dst_mock = Mock()
    client.copy_db_cluster_snapshot(snapshot_src_mock, snapshot_dst_mock)


if __name__ == "__main__":
    #test_provision_subnet_group()
    #test_provision_db_parameter_group()
    #test_provision_db_cluster_parameter_group()
    #test_provision_cluster()
    #test_provision_db_instance()
    test_copy_db_snapshot()
