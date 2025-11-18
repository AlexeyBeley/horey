"""
Testing selenium api
"""

import sys, os
import pytest
from horey.selenium_api.aucton_api import AuctionAPI

auction_api = AuctionAPI()


# print(os.path.abspath(sys.modules[AuctionAPI.__module__].__file__))

# pylint: disable= missing-function-docstring


@pytest.mark.done
def test_init_providers_from_db():
    auction_api.init_providers_from_db()


@pytest.mark.done
def test_write_providers_to_db():
    auction_api.write_providers_to_db()


@pytest.mark.done
def test_write_auction_events_to_db():
    auction_api.write_auction_events_to_db()


@pytest.mark.done
def test_write_lots_to_db():
    auction_api.write_lots_to_db()


@pytest.mark.done
def test_update_info():
    auction_api.update_info()


@pytest.mark.done
def test_print_coming_auction():
    auction_api.print_coming_auction()


@pytest.mark.unit
def test_init_auction_events_from_db():
    auction_api.init_auction_events_from_db()


@pytest.mark.unit
def test_update_info_auction_event_async():
    auction_api.update_info_auction_event_async(26)


@pytest.mark.skip("Use with caution!")
def test_delete_auction_event_with_lots():
    auction_api.delete_auction_event_with_lots(25)


@pytest.mark.unit
def test_update_info_provider_auction_events_asynchronous():
    auction_api.update_info_provider_auction_events_asynchronous(1)


# @pytest.mark.skip("Use with caution!")
@pytest.mark.unit
def test_auction_event_manual_update():
    auction_api.auction_event_manual_update()


@pytest.mark.unit
def test_add_column_after_column():
    auction_api.add_column_after_column()
