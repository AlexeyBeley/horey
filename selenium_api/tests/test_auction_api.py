"""
Testing selenium api
"""

import pytest
from horey.selenium_api.aucton_api import AuctionAPI

auction_api = AuctionAPI()

# pylint: disable= missing-function-docstring


@pytest.mark.wip
def test_write_providers_to_db():
    auction_api.write_providers_to_db()


@pytest.mark.done
def test_init_providers():
    auction_api.init_providers()


@pytest.mark.wip
def test_write_auction_events_to_db():
    auction_api.write_auction_events_to_db()
