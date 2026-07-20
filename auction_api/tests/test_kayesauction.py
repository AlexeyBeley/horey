"""
Testing selenium api
"""

import pytest
from horey.auction_api.kayesauction import Kayesauction
from horey.auction_api.auction_event import AuctionEvent


# pylint: disable= missing-function-docstring


@pytest.mark.unit
def test_init_auction_events():
    auction = Kayesauction()
    assert auction.init_auction_events({})


@pytest.mark.unit
def test_init_auction_event_lots():
    auction = Kayesauction()
    auction_event = AuctionEvent()
    auction_event.url = "https://kayesauctions.hibid.com/catalog/740048/special-offsite-leasing-co--repo-auction-june-1--2026"
    auction_event.provinces = "manitoba"
    assert auction.init_auction_event_lots(auction_event)
