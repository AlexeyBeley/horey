"""
Testing selenium api
"""

import pytest
from horey.selenium_api.aucton_api import AuctionAPI

auction_api = AuctionAPI()

# pylint: disable= missing-function-docstring


@pytest.mark.done
def test_provision_db_providers():
    auction_api.provision_db_providers()


@pytest.mark.wip
def test_init_all_providers():
    auction_api.init_all_providers()


