import os
import sys
import pdb

sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(0, "/Users/alexeybe/private/IP/ip")
sys.path.insert(0, "/Users/alexeybe/private/aws_api/ignore")
sys.path.insert(0, "/Users/alexeybe/private/aws_api/src/base_entities")
sys.path.insert(0, "/Users/alexeybe/private/aws_api/src/aws_clients")

from ecr_client import ECRClient
import ignore_me
import logging
logger = logging.Logger(__name__)
from aws_account import AWSAccount

tested_account = ignore_me.acc_default
AWSAccount.set_aws_account(tested_account)


cache_base_path = os.path.join(os.path.expanduser("~"), f"private/aws_api/ignore/cache_objects_{tested_account.name}")


def test_init_ecr_client():
    assert isinstance(ECRClient(), ECRClient)


def test_get_authorization_info():
    client = ECRClient()
    assert len(client.get_authorization_info()) == 1


if __name__ == "__main__":
    test_get_authorization_info()
