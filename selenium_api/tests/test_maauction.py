"""
Testing selenium api
"""

import pytest
from horey.selenium_api.maauction import MAauction


# pylint: disable= missing-function-docstring


@pytest.mark.unit
def test_load_page():
    auction = MAauction()
    assert auction.load_page_items(1)


@pytest.mark.unit
def test_get_page_count():
    auction = MAauction()
    assert auction.get_page_count()


@pytest.mark.unit
def test_init_all_items():
    auction = MAauction()
    ret = auction.init_all_items()

    ret = sorted(ret, key=lambda x: x.high_bid)
    for x in ret: print(f"{x.high_bid} : {x.name}")


@pytest.mark.unit
def test_init_auction_events():
    auction = MAauction()
    ret = auction.init_auction_events()
    assert ret


@pytest.mark.unit
def test_init_auction_lots():
    auction = MAauction()
    ret = auction.init_auction_events()
    for auction_event in ret:
        lots = auction.init_auction_event_lots(auction_event)
        assert isinstance(lots, list)
