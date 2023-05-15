"""
SSH API tests

"""

import os
import datetime
from horey.common_utils.common_utils import CommonUtils

# pylint: disable= missing-function-docstring


def test_int_to_str():
    assert CommonUtils.int_to_str(1) == "1"
    assert CommonUtils.int_to_str(1000) == "1,000"
    assert CommonUtils.int_to_str(1000000) == "1,000,000"
    assert CommonUtils.int_to_str(-1000) == "-1,000"


def test_bytes_to_str():
    assert CommonUtils.bytes_to_str(11) == "11 Bytes"
    assert CommonUtils.bytes_to_str(1000) == "1000 Bytes"
    assert CommonUtils.bytes_to_str(10000000) == "9.54 MiB"
    assert CommonUtils.bytes_to_str(100000000000000) == "90.95 TiB"


def test_timestamp_to_datetime():
    assert CommonUtils.timestamp_to_datetime(0) == datetime.datetime(
        1970, month=1, day=1, hour=2
    )


def test_generate_ed25519_key():
    self_dir_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(self_dir_path, "tmp.key")
    if os.path.exists(file_path):
        os.remove(file_path)
    CommonUtils.generate_ed25519_key("horey_horey@gmail.com", file_path)


if __name__ == "__main__":
    test_generate_ed25519_key()
