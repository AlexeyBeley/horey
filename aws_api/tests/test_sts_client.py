"""
Test SES client.

"""

import os
import pytest

# pylint: disable=missing-function-docstring

from horey.aws_api.aws_clients.sts_client import STSClient


STSClient().main_cache_dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..",
            "ignore",
            "cache"
        )
    )

client = STSClient()
@pytest.mark.todo
def test_init_ses_client():
    assert isinstance(STSClient(), STSClient)

@pytest.mark.todo
def test_decode_authorization_message():
    src_line = ""
    ret = client.decode_authorization_message(src_line)
    print(ret)
