import sys
import pdb
import datetime
sys.path.insert(0, "/Users/alexeybe/private/aws_api/src/base_entities")

from common_utils import CommonUtils

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
    assert CommonUtils.timestamp_to_datetime(0) == datetime.datetime(1970, month=1, day=1, hour=2)
