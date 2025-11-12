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


@pytest.mark.done
def test_report_auctions_html():
    auction_api.report_auctions_html()
