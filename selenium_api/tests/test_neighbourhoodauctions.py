"""
Testing selenium api
"""

import pytest
from horey.selenium_api.neighbourhoodauctions import Neighbourhoodauctions
from horey.selenium_api.auction_event import AuctionEvent


# pylint: disable= missing-function-docstring


@pytest.mark.unit
def test_init_auction_events():
    auction = Neighbourhoodauctions()
    assert auction.init_auction_events({})


@pytest.mark.wip
def test_yiel():
    auction = Neighbourhoodauctions()
    auction_event = AuctionEvent()
    auction_event.url = "https://www.icollector.com/APR-JUN-Estate-Collectibles-Auction-Winnipeg-MB_as115310"
    auction_event.provinces = "manitoba"
    for x in auction.yield_auction_event_lots(auction_event):
        assert x
