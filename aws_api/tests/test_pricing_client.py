"""
Test Pricing client
"""
import os
import datetime
import pytest

from horey.aws_api.aws_clients.pricing_client import PricingClient
from horey.aws_api.base_entities.region import Region
from horey.common_utils.common_utils import CommonUtils


mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


PricingClient().main_cache_dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..",
            "ignore",
            "cache"
        )
    )

# pylint: disable= missing-function-docstring

@pytest.mark.wip
def test_init_pricing_client():
    assert isinstance(PricingClient(), PricingClient)

@pytest.mark.wip
def test_yield_price_lists():
    client = PricingClient()
    price_list = None
    region = Region.get_region("us-west-2")
    for price_list in client.yield_price_lists(region=region, filters_req={"ServiceCode":"AmazonEC2",
                             "EffectiveDate": datetime.datetime.now(),
                             "RegionCode": region.region_mark,
                             "CurrencyCode": "USD"}):
        break
    assert price_list.version is not None
