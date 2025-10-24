"""
Testing selenium api
"""

import pytest
from horey.selenium_api.mcsherryauction import Mcsherryauction

auction = Mcsherryauction()

# pylint: disable= missing-function-docstring


@pytest.mark.unit
def test_load_page():
    assert auction.load_page_items(1)


@pytest.mark.unit
def test_get_page_count():
    assert auction.get_page_count()

@pytest.mark.wip
def test_init_all_items():
    assert auction.init_all_items()



