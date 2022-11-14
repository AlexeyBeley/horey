import os
import pdb

from horey.aws_api.aws_clients.route53_client import Route53Client
from horey.aws_api.aws_api_configuration_policy import AWSAPIConfigurationPolicy
from horey.h_logger import get_logger
from horey.common_utils.common_utils import CommonUtils

from horey.aws_api.base_entities.aws_account import AWSAccount

logger = get_logger()

configuration = AWSAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "..",
        "ignore",
        "aws_api_configuration_values.py",
    )
)
configuration.init_from_file()

accounts = CommonUtils.load_object_from_module(configuration.accounts_file, "main")
AWSAccount.set_aws_account(accounts[configuration.aws_api_account])


def test_init_route53_client():
    assert isinstance(Route53Client(), Route53Client)


if __name__ == "__main__":
    test_init_route53_client()
