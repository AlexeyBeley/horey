"""
Test aws ecr client.

"""

import os

from horey.aws_api.aws_clients.ecr_client import ECRClient
from horey.h_logger import get_logger
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.common_utils.common_utils import CommonUtils

configuration_values_file_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "h_logger_configuration_values.py")
logger = get_logger(configuration_values_file_full_path=configuration_values_file_full_path)

accounts_file_full_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "aws_api_managed_accounts.py"))

accounts = CommonUtils.load_object_from_module(accounts_file_full_path, "main")
AWSAccount.set_aws_account(accounts["1111"])
AWSAccount.set_aws_region(accounts["1111"].regions["us-west-2"])

mock_values_file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"))
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


def test_init_ecr_client():
    """
    Base init check.

    @return:
    """

    assert isinstance(ECRClient(), ECRClient)


def test_get_authorization_info():
    """
    Test getting authorization info used by docker service.

    @return:
    """

    client = ECRClient()
    assert len(client.get_authorization_info()) == 1


def test_tag_image():
    """
    Tag image with new tags.

    @return:
    """

    client = ECRClient()
    repos = client.get_region_repositories(accounts["1111"].regions["us-west-2"])
    images = client.get_all_images(repos[4])
    client.tag_image(images[3], ["test_tag"])


if __name__ == "__main__":
    # test_get_authorization_info()
    test_tag_image()
