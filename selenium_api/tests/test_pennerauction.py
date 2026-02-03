"""
Testing selenium api
"""

import pytest
from horey.selenium_api.pennerauction import Pennerauction
from horey.selenium_api.auction_event import AuctionEvent


# pylint: disable= missing-function-docstring


@pytest.mark.unit
def test_init_auction_events():
    auction = Pennerauction()
    assert auction.init_auction_events()



@pytest.mark.wip
def test_init_auction_event():
    auction = Pennerauction()
    auction_event = AuctionEvent()
    auction_event.url = "https://pennerauctions.hibid.com/catalog/710766"
    assert auction.init_auction_event(auction_event)

@pytest.mark.unit
def test_init_auction_event_lots():
    auction = Pennerauction()
    auction_event = AuctionEvent()
    auction_event.provinces = "manitoba"
    auction_event.url = "https://pennerauctions.hibid.com/catalog/710766"
    assert auction.init_auction_event_lots(auction_event)
