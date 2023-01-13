"""
Testing EC2 client

"""

import os
from unittest.mock import Mock
from horey.aws_api.aws_clients.ec2_client import EC2Client
from horey.h_logger import get_logger
from horey.common_utils.common_utils import CommonUtils

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.ec2_launch_template import EC2LaunchTemplate
from horey.aws_api.aws_services_entities.ec2_security_group import EC2SecurityGroup
from horey.aws_api.base_entities.region import Region

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

# pylint: disable= missing-function-docstring


def test_init_ec2_client():
    assert isinstance(EC2Client(), EC2Client)


DICT_CREATE_SECURITY_GROUP_REQUEST = {
    "Description": "sg-test-group",
    "GroupName": "sg_test-group",
}


def test_create_security_group():
    client = EC2Client()
    ret = client.raw_create_security_group(DICT_CREATE_SECURITY_GROUP_REQUEST)
    assert ret is not None


def test_provision_security_group():
    """
    Test provisioning.

    @return:
    """

    client = EC2Client()
    security_group = EC2SecurityGroup(DICT_CREATE_SECURITY_GROUP_REQUEST)
    security_group.region = Region.get_region("us-west-2")
    security_group.ip_permissions = [
        {
            "IpProtocol": "tcp",
            "FromPort": 8080,
            "ToPort": 8080,
            "IpRanges": [{"CidrIp": "1.1.1.1/32"}],
        },
    ]
    client.provision_security_group(security_group)


def test_provision_security_group_revoke():
    """
    Test provisioning.

    @return:
    """

    client = EC2Client()
    security_group = EC2SecurityGroup(DICT_CREATE_SECURITY_GROUP_REQUEST)
    security_group.region = Region.get_region("us-west-2")
    security_group.ip_permissions = [
        {
            "IpProtocol": "tcp",
            "FromPort": 8080,
            "ToPort": 8081,
            "IpRanges": [{"CidrIp": "1.1.1.1/32"}],
        },
    ]
    client.provision_security_group(security_group)


def test_provision_security_group_complex():
    """
    Test:
    * Replace one rule with the other
    * Change the description
    * Remove the description

    @return:
    """

    client = EC2Client()
    security_group = EC2SecurityGroup(DICT_CREATE_SECURITY_GROUP_REQUEST)
    security_group.region = Region.get_region("us-west-2")
    security_group.ip_permissions = [
        {
            "IpProtocol": "tcp",
            "FromPort": 8080,
            "ToPort": 8080,
            "IpRanges": [
                {"CidrIp": "8.8.8.8/32", "Description": "test"},
            ],
        },
        {
            "IpProtocol": "tcp",
            "FromPort": 8080,
            "ToPort": 8080,
            "IpRanges": [
                {"CidrIp": "1.1.1.1/32", "Description": "test"},
            ],
        },
        {
            "IpProtocol": "tcp",
            "FromPort": 8080,
            "ToPort": 8080,
            "IpRanges": [
                {"CidrIp": "1.1.1.3/32", "Description": "test"},
            ],
        },
    ]
    client.provision_security_group(security_group)

    security_group = EC2SecurityGroup(DICT_CREATE_SECURITY_GROUP_REQUEST)
    security_group.region = Region.get_region("us-west-2")
    security_group.ip_permissions = [
        {
            "IpProtocol": "tcp",
            "FromPort": 8080,
            "ToPort": 8080,
            "IpRanges": [
                {"CidrIp": "8.8.8.8/32", "Description": "test-1"},
            ],
        },
        {
            "IpProtocol": "tcp",
            "FromPort": 8080,
            "ToPort": 8080,
            "IpRanges": [{"CidrIp": "1.1.1.1/32"}],
        },
        {
            "IpProtocol": "tcp",
            "FromPort": 8080,
            "ToPort": 8080,
            "IpRanges": [
                {"CidrIp": "1.1.1.2/32", "Description": "test"},
            ],
        },
    ]
    client.provision_security_group(security_group)


SECURITY_GROUP_ID = ""
DICT_AUTHORIZE_SECURITY_GROUP_INGRESS_REQUEST_1 = {
    "GroupId": SECURITY_GROUP_ID,
    "IpPermissions": [
        {
            "IpProtocol": "tcp",
            "FromPort": 8080,
            "ToPort": 8080,
            "IpRanges": [{"CidrIp": "1.1.1.1/32"}],
        },
    ],
}

DICT_AUTHORIZE_SECURITY_GROUP_INGRESS_REQUEST_2 = {
    "GroupId": SECURITY_GROUP_ID,
    "IpPermissions": [
        {
            "IpProtocol": "tcp",
            "FromPort": 80,
            "ToPort": 80,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        },
    ],
}


def test_get_all_security_groups():
    client = EC2Client()
    sec_groups = client.get_all_security_groups()
    assert isinstance(sec_groups, list)


def test_raw_create_managed_prefix_list():
    request = {
        "PrefixListName": "pl_test_name",
        "Entries": [{"Cidr": "2.2.2.2/32", "Description": "string"}],
        "MaxEntries": 1000,
        "AddressFamily": "IPv4",
    }

    for region in AWSAccount.get_aws_account().regions.values():
        AWSAccount.set_aws_region(region)

        prefix_list_name = "test"

        request = {
            "PrefixListName": prefix_list_name,
            "MaxEntries": 60,
            "AddressFamily": "IPv4",
            "TagSpecifications": [
                {
                    "ResourceType": "prefix-list",
                    "Tags": [{"Key": "Name", "Value": prefix_list_name}],
                },
            ],
        }
        client = EC2Client()
        ret = client.raw_create_managed_prefix_list(request, add_client_token=False)
        assert isinstance(ret, dict)


def test_raw_modify_managed_prefix_list():
    client = EC2Client()
    pl_id = "pl-0d1adbd1928158a65"
    base_version = 7
    request = {
        "CurrentVersion": base_version,
        "PrefixListId": pl_id,
        "AddEntries": [{"Cidr": "1.1.1.1/32", "Description": "string_1"}],
    }
    ret = client.raw_modify_managed_prefix_list(request)
    assert isinstance(ret, dict)
    print(ret)
    base_version += 1

    request = {
        "CurrentVersion": base_version,
        "PrefixListId": pl_id,
        "RemoveEntries": [{"Cidr": "1.1.1.1/32"}],
    }

    ret = client.raw_modify_managed_prefix_list(request)
    assert isinstance(ret, dict)


def test_raw_modify_managed_prefix_list_add():
    client = EC2Client()
    pl_id = ""
    base_version = 7
    request = {
        "CurrentVersion": base_version,
        "PrefixListId": pl_id,
        "AddEntries": [{"Cidr": "1.1.1.1/32", "Description": "string_1"}],
    }
    ret = client.raw_modify_managed_prefix_list(request)
    assert isinstance(ret, dict)


def test_raw_describe_managed_prefix_list_by_id():
    pl_id = "pl-111111111"
    client = EC2Client()
    ret = client.raw_describe_managed_prefix_list(Region.get_region("us-west-2"), pl_id=pl_id)
    print(ret)


def test_raw_describe_managed_prefix_list_by_name():
    prefix_list_name = "pl_horey_test-name"
    client = EC2Client()
    ret = client.raw_describe_managed_prefix_list(Region.get_region("us-west-2"), prefix_list_name=prefix_list_name)
    print(ret)


def test_provision_launch_template():
    ec2_client = EC2Client()
    iam_instance_profile = Mock()
    iam_instance_profile.arn = mock_values["iam_instance_profile.arn"]

    security_group = Mock()
    security_group.id = mock_values["security_group.id"]

    ami = Mock()
    ami.id = mock_values["ami.id"]

    subnet = Mock()
    subnet.id = mock_values["subnet.id"]

    ssh_key_pair = Mock()
    ssh_key_pair.name = mock_values["ssh_key_pair.name"]
    user_data = ec2_client.generate_user_data_from_file(
        "ecs_container_instance_user_data.sh"
    )

    # filter_request = dict()
    # filter_request["Filters"] = [{'Name': 'name',
    #                                  'Values': [
    #                                      "amzn2-ami-ecs-hvm-2.0.20201209-x86_64-ebs",
    #                                  ]}]
    # ami = self.aws_api.ec2_client.get_region_amis(self.configuration.region, custom_filters=filter_request)[0]

    launch_template = EC2LaunchTemplate({})
    launch_template.name = "test_launch_template_name"
    launch_template.tags = [{"Key": "lvl", "Value": "tst"}]
    launch_template.region = AWSAccount.get_aws_region()
    launch_template.tags.append({"Key": "Name", "Value": launch_template.name})
    launch_template.launch_template_data = {
        "EbsOptimized": False,
        "IamInstanceProfile": {"Arn": iam_instance_profile.arn},
        "BlockDeviceMappings": [
            {"DeviceName": "/dev/xvda", "Ebs": {"VolumeSize": 40, "VolumeType": "gp2"}}
        ],
        "NetworkInterfaces": [
            {
                "AssociatePublicIpAddress": True,
                "DeleteOnTermination": True,
                "DeviceIndex": 0,
                "Groups": [
                    security_group.id,
                ],
                "SubnetId": subnet.id,
            },
        ],
        "ImageId": ami.id,
        "InstanceType": "c5.large",
        "KeyName": ssh_key_pair.name,
        "Monitoring": {"Enabled": False},
        "UserData": user_data,
    }

    ec2_client.provision_launch_template(launch_template)
    assert launch_template.id is not None


def test_find_launch_template():
    launch_template = Mock()
    launch_template.region = Region.get_region("us-west-2")
    launch_template.name = mock_values["launch_template.name"]

    ec2_client = EC2Client()
    ret = ec2_client.find_launch_template(launch_template)
    assert ret is not None


if __name__ == "__main__":
    # test_provision_security_group()
    # test_provision_security_group_revoke()
    # test_provision_security_group_complex()
    # test_provision_launch_template()

    # test_raw_modify_managed_prefix_list()
    # test_raw_describe_managed_prefix_list_by_id()
    # test_raw_describe_managed_prefix_list_by_name()
    test_find_launch_template()
