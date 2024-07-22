"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  ipaddr:/ /home/ubuntu/efs
"""
import traceback
import pytest
from horey.h_logger import get_logger, get_raw_logger

logger = get_logger()

# pylint: disable= missing-function-docstring

@pytest.mark.skip(reason="")
def test_log_multiline():
    try:
        raise RuntimeError("test")
    except Exception:
        logger.exception(traceback.format_exc(8))


@pytest.mark.wip
def test_get_raw_logger():
    assert get_raw_logger("test") is get_raw_logger("test")


@pytest.mark.wip
def test_logger_raw_output(caplog):
    raw_logger = get_raw_logger("test")
    raw_logger.info("testing output raw logger")
    assert "testing output raw logger" in caplog.text
