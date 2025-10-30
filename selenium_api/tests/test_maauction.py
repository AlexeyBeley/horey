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




