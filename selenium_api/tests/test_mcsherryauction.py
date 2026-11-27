"""
Testing selenium api
"""

import pytest
from horey.selenium_api.mcsherryauction import Mcsherryauction


# pylint: disable= missing-function-docstring


@pytest.mark.done
def test_load_page():
    auction = Mcsherryauction()
    assert auction.load_page_items(1)


@pytest.mark.done
def test_get_page_count():
    auction = Mcsherryauction()
    assert auction.get_page_count()


@pytest.mark.done
def test_init_all_items():
    auction = Mcsherryauction()
    ret = auction.init_all_items()

    ret = sorted(ret, key=lambda x: x.high_bid)
    for x in ret: print(f"{x.high_bid} : {x.name}")




