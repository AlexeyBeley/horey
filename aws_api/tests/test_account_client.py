"""
Test aws account client

"""

import os
import pytest

from horey.aws_api.aws_clients.account_client import AccountClient

AccountClient().main_cache_dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..",
            "ignore",
            "cache"
        )
    )

# pylint: disable= missing-function-docstring

@pytest.mark.wip
def test_init_client():
    """
    Base init check.

    @return:
    """

    assert isinstance(AccountClient(), AccountClient)

@pytest.mark.wip
def test_get_all_regions():
    client = AccountClient()
    regions = client.get_all_regions(update_info=True)
    assert regions is not None
