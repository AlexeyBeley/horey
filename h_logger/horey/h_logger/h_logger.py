"""
logging handler
"""
import logging


handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s:%(filename)s:%(lineno)s: %(message)s")
handler.setFormatter(formatter)
_logger = logging.getLogger("main")
_logger.setLevel("INFO")
_logger.addHandler(handler)


def get_logger():
    """
    Reuse logger
    :return:
    """
    return _logger
