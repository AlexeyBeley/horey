"""
Testing acm client

"""

import os
import pytest
from horey.aws_api.aws_clients.application_auto_scaling_client import ApplicationAutoScalingClient


ApplicationAutoScalingClient().main_cache_dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..",
            "ignore",
            "cache"
        )
    )

# pylint: disable= missing-function-docstring

@pytest.mark.todo
def test_init_client():
    assert isinstance(ApplicationAutoScalingClient(), ApplicationAutoScalingClient)


@pytest.mark.todo
def test_yield_policies():
    client = ApplicationAutoScalingClient()
    for x in client.yield_policies():
        breakpoint()
        assert x
        break
