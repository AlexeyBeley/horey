"""
Testing AutoScalingClient client.

"""

import os

from horey.aws_api.aws_clients.auto_scaling_client import AutoScalingClient
from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.common_utils.common_utils import CommonUtils
from horey.aws_api.base_entities.region import Region
from horey.aws_api.aws_clients.ec2_client import EC2Client
from horey.aws_api.aws_services_entities.ec2_instance import EC2Instance
from horey.aws_api.aws_services_entities.auto_scaling_group import AutoScalingGroup

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

# accounts["1111"].regions["us-east-1"] = Region.get_region("us-east-1")
# accounts["1111"].regions["eu-central-1"] = Region.get_region("eu-central-1")

AWSAccount.set_aws_account(accounts["1111"])
AWSAccount.set_aws_region(accounts["1111"].regions["us-west-2"])

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

client = AutoScalingClient()


# pylint: disable= missing-function-docstring


def test_init_client():
    assert isinstance(AutoScalingClient(), AutoScalingClient)


def test_detach_instances():
    region = Region.get_region("us-east-1")
    inst_ids = [
                ]
    asg = AutoScalingGroup({})
    asg.name = mock_values["autoscaling_group_name_detach_instances_prod"]
    asg.region = region
    asg.desired_count = 100
    client.detach_instances(asg, inst_ids, decrement=True)

    ec2_client = EC2Client()
    for inst_id in inst_ids:
        ec2_instance = EC2Instance({})
        ec2_instance.region = region
        ec2_instance.id = inst_id
        ec2_client.dispose_instance(ec2_instance)

if __name__ == "__main__":
    test_init_client()
    test_detach_instances()
