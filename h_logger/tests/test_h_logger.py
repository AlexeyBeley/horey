"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  ipaddr:/ /home/ubuntu/efs
"""
import os.path
import traceback
import pytest
from horey.h_logger import get_logger, get_raw_logger
from horey.h_logger.h_logger import StaticData


# pylint: disable= missing-function-docstring

@pytest.mark.todo
def test_log_multiline():
    logger = get_logger()
    try:
        raise RuntimeError("test")
    except Exception:
        logger.exception(traceback.format_exc(8))


@pytest.mark.todo
def test_get_raw_logger():
    assert get_raw_logger("test") is get_raw_logger("test")


@pytest.mark.todo
def test_logger_raw_output(caplog):
    raw_logger = get_raw_logger("test")
    raw_logger.info("testing output raw logger")
    assert "testing output raw logger" in caplog.text


@pytest.mark.wip
def test_get_logger_with_configuration():
    StaticData.logger = None
    logger = get_logger(configuration_file_full_path=os.path.join(os.path.dirname(__file__), "configuration.py"))
    logger.info("testing output raw logger")
