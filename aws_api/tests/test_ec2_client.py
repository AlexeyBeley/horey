import os
import pdb

from horey.aws_api.aws_clients.ec2_client import EC2Client
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.h_logger import get_logger
from horey.common_utils.common_utils import CommonUtils

from horey.aws_api.base_entities.aws_account import AWSAccount

logger = get_logger()

configuration = AWSAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                 "aws_api_configuration_values.py"))
configuration.init_from_file()

accounts = CommonUtils.load_object_from_module(configuration.accounts_file, "main")
AWSAccount.set_aws_account(accounts[configuration.aws_api_account])


def test_init_ec2_client():
    assert isinstance(EC2Client(), EC2Client)


DICT_CREATE_SECURITY_GROUP_REQUEST = {
    "Description": "test-alexey-group",
    "GroupName": "test-alexey-group",
}


def test_create_security_group():
    client = EC2Client()
    ret = client.raw_create_security_group(DICT_CREATE_SECURITY_GROUP_REQUEST)
    # pdb.set_trace()


SECURITY_GROUP_ID = ""
DICT_AUTHORIZE_SECURITY_GROUP_INGRESS_REQUEST_1 = {
    "GroupId": SECURITY_GROUP_ID,
    "IpPermissions": [
        {"IpProtocol": "tcp",
         "FromPort": 8080,
         "ToPort": 8080,
         "IpRanges": [{"CidrIp": "1.1.1.1/32"}]},
    ]}

DICT_AUTHORIZE_SECURITY_GROUP_INGRESS_REQUEST_2 = {
    "GroupId": SECURITY_GROUP_ID,
    "IpPermissions": [
        {"IpProtocol": "tcp",
         "FromPort": 80,
         "ToPort": 80,
         "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
    ]}


def test_get_all_security_groups():
    client = EC2Client()
    sec_groups = client.get_all_security_groups()
    sec_groups[5]


def test_authorize_security_group_ingress():
    client = EC2Client()
    pdb.set_trace()
    client.authorize_security_group_ingress(DICT_AUTHORIZE_SECURITY_GROUP_INGRESS_REQUEST_1)
    client.authorize_security_group_ingress(DICT_AUTHORIZE_SECURITY_GROUP_INGRESS_REQUEST_2)


def test_raw_create_managed_prefix_list():
    request = {"PrefixListName": "pl_staging_cloud_hive_public_outgoing",
               "Entries": [
                   {
                       "Cidr": "2.2.2.2/32",
                       "Description": "string"
                   }],
               "MaxEntries": 1000,
               "AddressFamily": "IPv4",
               }

    for region in AWSAccount.get_aws_account().regions.values():
        AWSAccount.set_aws_region(region)

        prefix_list_name = "test"

        request = {"PrefixListName": prefix_list_name,
               "MaxEntries": 60,
               "AddressFamily": "IPv4",
               "TagSpecifications": [
                                       {
                                           'ResourceType': 'prefix-list',
                                           'Tags': [
                                               {
                                                   'Key': 'Name',
                                                   'Value': prefix_list_name
                                               }
                                           ]
                                       },
                                   ],
               }
        client = EC2Client()
        ret = client.raw_create_managed_prefix_list(request, add_client_token=False)
        assert isinstance(ret, dict)
        print(ret)
        #pdb.set_trace()


def test_raw_modify_managed_prefix_list():
    client = EC2Client()
    pl_id = "pl-0d1adbd1928158a65"
    base_version = 7
    request = {
        "CurrentVersion": base_version,
        "PrefixListId": pl_id,
        "AddEntries": [
            {
                "Cidr": "1.1.1.1/32",
                "Description": "string_1"
            }
        ]
    }
    ret = client.raw_modify_managed_prefix_list(request)
    assert isinstance(ret, dict)
    print(ret)
    base_version += 1

    request = {
        "CurrentVersion": base_version,
        "PrefixListId": pl_id,
        "RemoveEntries": [
            {
                "Cidr": "1.1.1.1/32"
            }
        ]
    }

    ret = client.raw_modify_managed_prefix_list(request)
    assert isinstance(ret, dict)
    print(ret)
    #pdb.set_trace()


def test_raw_modify_managed_prefix_list_add():
    client = EC2Client()
    pl_id = ""
    base_version = 7
    request = {
        "CurrentVersion": base_version,
        "PrefixListId": pl_id,
        "AddEntries": [
            {
                "Cidr": "1.1.1.1/32",
                "Description": "string_1"
            }
        ]
    }
    ret = client.raw_modify_managed_prefix_list(request)
    assert isinstance(ret, dict)
    print(ret)

def test_raw_describe_managed_prefix_list_by_id():
    pl_id = "pl-0d1adbd1928158a65"
    client = EC2Client()
    ret = client.raw_describe_managed_prefix_list(pl_id=pl_id)
    print(ret)


def test_raw_describe_managed_prefix_list_by_name():
    prefix_list_name = "pl_prod_cloud_hive_public_outgoing"
    client = EC2Client()
    ret = client.raw_describe_managed_prefix_list(prefix_list_name=prefix_list_name)
    print(ret)


if __name__ == "__main__":
    #test_create_security_group()
    test_raw_create_managed_prefix_list()

    #test_raw_modify_managed_prefix_list()
    #test_raw_describe_managed_prefix_list_by_id()
    #test_raw_describe_managed_prefix_list_by_name()
