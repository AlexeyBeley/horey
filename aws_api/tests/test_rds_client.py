import os
import sys

from horey.aws_api.aws_clients.rds_client import RDSClient
from horey.aws_api.aws_services_entities.rds_db_cluster import RDSDBCluster
from horey.aws_api.aws_services_entities.rds_db_subnet_group import RDSDBSubnetGroup

import pdb
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


def test_init_acm_client():
    assert isinstance(RDSClient(), RDSClient)


def test_provision_cluster():
    client = RDSClient()
    cluster = RDSDBCluster({})
    cluster.region = AWSAccount.get_aws_region()

    cluster.availability_zones = []
    cluster.backup_retention_period = 35
    cluster.database_name = ""
    cluster.db_cluster_identifier = ""
    cluster.vpc_security_group_ids = ""
    cluster.engine = "aurora-mysql"
    cluster.engine_version = "5.7.mysql_aurora.2.09.2"
    cluster.port = 3306

    cluster.master_username = "admin"
    cluster.master_user_password = ""
    cluster.preferred_backup_window = "09:23-09:53"
    cluster.preferred_maintenance_window = "sun:03:30-sun:04:00"
    cluster.storage_encrypted = True
    cluster.kms_key_id = True
    cluster.engine_mode = "provisioned"

    cluster.deletion_protection = True
    cluster.copy_tags_to_snapshot = True

    cluster.tags = [
        {
            'Key': 'lvl',
            'Value': "tst"
        }, {
            'Key': 'name',
            'Value': cluster.db_cluster_identifier
        }
    ]

    ret = client.provision_db_cluster(cluster)
    pdb.set_trace()

    assert cluster.arn is not None


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


if __name__ == "__main__":
    #test_provision_cluster()
    test_provision_subnet_group()

