"""
logging handler
"""
import logging


handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s:%(name)s:%(message)s")
handler.setFormatter(formatter)
_logger = logging.getLogger()
_logger.setLevel("INFO")
_logger.addHandler(handler)


def get_logger():
    """
    Reuse logger
    :return:
    """
    return _logger
