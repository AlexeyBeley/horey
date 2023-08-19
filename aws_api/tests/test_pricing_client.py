"""
Testing pricing client functionality

"""
import os

from horey.aws_api.aws_clients.pricing_client import PricingClient
from horey.aws_api.base_entities.region import Region

from horey.h_logger import get_logger

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
        "aws_api_configuration_values_all_access.py",
    )
)

# pylint: disable= missing-function-docstring


def test_init_cloudfront_client():
    assert isinstance(PricingClient(), PricingClient)

def test_get_price_list_urls():
    """

    :return:
    """
    client = PricingClient()
    ret = client.get_price_list_urls("AWSLambda", Region.get_region("us-east-1"))
    assert len(ret) == 1

def test_get_services():
    client = PricingClient()
    ret = client.get_services()
    assert len(ret) > 0

if __name__ == "__main__":
    # test_init_cloudfront_client()
    # test_get_services()
    test_get_price_list_urls()
