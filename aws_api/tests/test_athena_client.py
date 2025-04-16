"""
Test athena client

"""

import os
import pytest
from horey.aws_api.aws_clients.athena_client import AthenaClient


AthenaClient().main_cache_dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..",
            "ignore",
            "cache"
        )
    )

# pylint: disable= missing-function-docstring

@pytest.mark.todo
def test_init_athena_client():
    assert isinstance(AthenaClient(), AthenaClient)

@pytest.mark.todo
def test_get():
    AthenaClient().get_all_template_entities()
    assert isinstance(AthenaClient(), AthenaClient)
