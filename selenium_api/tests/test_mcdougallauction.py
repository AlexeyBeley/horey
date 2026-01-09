"""
Testing selenium api
"""

import pytest
from horey.selenium_api.mcdougallauction import Mcdougallauction
from horey.selenium_api.auction_event import AuctionEvent


# pylint: disable= missing-function-docstring


@pytest.mark.unit
def test_init_auction_events():
    auction = Mcdougallauction()
    ret = auction.init_auction_events()
    assert len(ret) > 10


@pytest.mark.unit
def test_init_auction_event_lots():
    auction = Mcdougallauction()
    auction_event = AuctionEvent()
    auction_event.url = "https://www.mcdougallauction.com/auction-event.php?arg=241EB0B2-7F1F-4A79-A64C-5F5B678AA3F5"
    auction_event.provinces = "manitoba"
    assert auction.init_auction_event_lots(auction_event)


@pytest.mark.unit
def test_init_all_auction_event_lots():
    auction = Mcdougallauction()
    auction_events = auction.init_auction_events()
    for auction_event in auction_events:
        try:
            assert auction.init_auction_event_lots(auction_event)
        except Exception as error_inst:
            breakpoint()
            print(f"Error: {error_inst} Url: {auction_event.url}")
