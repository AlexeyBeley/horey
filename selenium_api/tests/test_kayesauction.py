"""
Testing selenium api
"""

import pytest
from horey.selenium_api.kayesauction import Kayesauction
from horey.selenium_api.auction_event import AuctionEvent


# pylint: disable= missing-function-docstring


@pytest.mark.unit
def test_init_auction_events():
    auction = Kayesauction()
    assert auction.init_auction_events()


@pytest.mark.unit
def test_init_auction_event_lots():
    auction = Kayesauction()
    auction_event = AuctionEvent()
    auction_event.url = "https://kayesauctions.hibid.com/catalog/692093/under-the-garage-keepers-act-november-24--2025"
    auction_event.provinces = "manitoba"
    assert auction.init_auction_event_lots(auction_event)
