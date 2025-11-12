"""
Testing selenium api
"""

import pytest
from horey.selenium_api.maauction import MAauction


# pylint: disable= missing-function-docstring


@pytest.mark.done
def test_load_page():
    auction = MAauction()
    assert auction.load_page_items(1)


@pytest.mark.done
def test_get_page_count():
    auction = MAauction()
    assert auction.get_page_count()


@pytest.mark.done
def test_init_all_items():
    auction = MAauction()
    ret = auction.init_all_items()

    ret = sorted(ret, key=lambda x: x.high_bid)
    for x in ret: print(f"{x.high_bid} : {x.name}")


@pytest.mark.done
def test_init_auction_events():
    auction = MAauction()
    ret = auction.init_auction_events()
    assert ret


@pytest.mark.done
def test_load_page_lot_elements():
    provider = MAauction()
    provider.connect()
    assert provider.load_page_lot_elements("https://www.maauctions.com/auctions/24840-november-1-2025-automotive-timed-vehicles-and-rvs-alberta")


@pytest.mark.done
def test_load_page_lots():
    provider = MAauction()
    provider.connect()
    ret = provider.load_page_lots("https://www.maauctions.com/auctions/24840-november-1-2025-automotive-timed-vehicles-and-rvs-alberta")
    assert ret


@pytest.mark.done
def test_init_auction_events_from_internal_url():
    provider = MAauction()
    provider.connect()
    ret = provider.init_auction_events_from_internal_url("https://www.jardineauctioneers.com/auctions/24884-december-4th-and-5th-2025-unreserved-equipment-trucks-trailers-light-vehicles-and-rv-live-2-day-auction-jardine")
    assert ret


@pytest.mark.done
def test_init_auction_lots():
    auction = MAauction()
    ret = auction.init_auction_events()
    for auction_event in ret:
        lots = auction.init_auction_event_lots(auction_event)
        assert isinstance(lots, list)
