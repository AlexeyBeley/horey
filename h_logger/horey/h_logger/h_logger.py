"""
logging handler
"""
import logging
from horey.h_logger.formatter import MultilineFormatter

handler = logging.StreamHandler()
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s:%(filename)s:%(lineno)s: %(message)s"
)
# formatter = logging.Formatter("[%(created)f] %(levelname)s:%(filename)s:%(lineno)s: %(message)s")
formatter = MultilineFormatter()
handler.setFormatter(formatter)
_logger = logging.getLogger("main")
_logger.setLevel("INFO")
_logger.addHandler(handler)

logger_initialized = False


def get_logger(configuration_values_file_full_path=None):
    """
    Reuse logger
    :return:
    """

    if not logger_initialized:
        if configuration_values_file_full_path is not None:
            # pylint: disable= import-outside-toplevel
            from horey.h_logger.h_logger_configuration_policy import (
                HLoggerConfigurationPolicy,
            )
            configuration = HLoggerConfigurationPolicy()
            configuration.configuration_file_full_path = (
                configuration_values_file_full_path
            )
            configuration.init_from_file()

            if configuration.error_level_file_path is not None:
                file_handler = logging.FileHandler(configuration.error_level_file_path)
                file_handler.setFormatter(formatter)
                file_handler.setLevel(logging.ERROR)
                _logger.addHandler(file_handler)

            _inited = True
    return _logger
