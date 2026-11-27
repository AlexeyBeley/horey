"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  ipaddr:/ /home/ubuntu/efs
"""
import os.path
import traceback
import pytest
from horey.h_logger import get_logger, get_raw_logger
from horey.h_logger.h_logger import StaticData


# pylint: disable= missing-function-docstring

@pytest.mark.wip
def test_log_multiline():
    logger = get_logger()
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
    raw_logger.info("test_logger_raw_output")
    assert "test_logger_raw_output" in caplog.text


@pytest.mark.wip
def test_get_logger_with_configuration():
    for handler in StaticData.logger.handlers:
        StaticData.logger.removeHandler(handler)
    StaticData.logger = None
    logger = get_logger(configuration_file_full_path=os.path.join(os.path.dirname(__file__), "configuration.py"))
    logger.info("test_get_logger_with_configuration")


@pytest.mark.wip
def test_get_logger_with_configuration_configure_existing_logger():
    get_logger()
    logger = get_logger(configuration_file_full_path=os.path.join(os.path.dirname(__file__), "configuration.py"))
    logger.info("test_get_logger_with_configuration_configure_existing_logger")


@pytest.mark.wip
def test_get_logger_with_configuration_same_file_reconfigure():
    get_logger(configuration_file_full_path=os.path.join(os.path.dirname(__file__), "configuration.py"))
    logger = get_logger(configuration_file_full_path=os.path.join(os.path.dirname(__file__), "configuration.py"))
    logger.info("test_get_logger_with_configuration_same_file_reconfigure")


@pytest.mark.wip
def test_get_logger_with_configuration_reinitialization_raise():
    get_logger()
    StaticData.logger = None
    with pytest.raises(RuntimeError, match=r".*There are handlers registered in this logger.*"):
        get_logger(configuration_file_full_path=os.path.join(os.path.dirname(__file__), "configuration.py"))


@pytest.mark.wip
def test_get_logger_with_configuration_reconfigure_raise():
    StaticData.logger = get_logger()
    for handler in StaticData.logger.handlers:
        StaticData.logger.removeHandler(handler)

    logger = get_logger(configuration_file_full_path=os.path.join(os.path.dirname(__file__), "configuration.py"))
    logger.info("test_get_logger_with_configuration_reconfigure_raise")

    with pytest.raises(ValueError, match=r".*Reconfiguring logger is not supported.*"):
        get_logger(configuration_file_full_path=os.path.join(os.path.dirname(__file__), "configuration_wrong.py"))
