"""
logging handler
"""
import logging

from horey.h_logger.formatter import MultilineFormatter
from horey.common_utils.common_utils import CommonUtils
from horey.h_logger.h_logger_configuration_policy import (
    HLoggerConfigurationPolicy
)


class StaticData:
    """
    Previous formatter:


    formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s:%(filename)s:%(lineno)s: %(message)s"
    )
    # formatter = logging.Formatter("[%(created)f] %(levelname)s:%(filename)s:%(lineno)s: %(message)s")

    """
    logger = None
    raw_loggers = {}
    formatter = MultilineFormatter()
    configuration_file_full_path = None


def init_logger_from_configuration(configuration_file_full_path):
    """
    File with config values in .py format.

    :param configuration_file_full_path:
    :return:
    """

    configuration = HLoggerConfigurationPolicy()
    config_values = CommonUtils.load_object_from_module(configuration_file_full_path, "main")
    for var, val in config_values.__dict__.items():
        setattr(configuration, var, val)

    if configuration.error_level_file_path is not None:
        file_handler = logging.FileHandler(configuration.error_level_file_path)
        file_handler.setFormatter(StaticData.formatter)
        file_handler.setLevel(logging.ERROR)
        StaticData.logger.addHandler(file_handler)
    if configuration.info_level_file_path is not None:
        file_handler = logging.FileHandler(configuration.info_level_file_path)
        file_handler.setFormatter(StaticData.formatter)
        file_handler.setLevel(logging.INFO)
        StaticData.logger.addHandler(file_handler)


def get_logger(configuration_file_full_path=None, name="horey"):
    """
    Reuse logger
    :return:
    """

    if StaticData.logger is None:
        StaticData.logger = logging.getLogger(name)
        if StaticData.logger.hasHandlers():
            if bool(StaticData.logger.handlers):
                raise RuntimeError(f"There are handlers registered in this logger. Looks like you are redefining same logger: {name=}")
        StaticData.logger.setLevel("INFO")
        handler = logging.StreamHandler()
        handler.setFormatter(StaticData.formatter)
        StaticData.logger.addHandler(handler)

    if configuration_file_full_path is not None:
        if StaticData.configuration_file_full_path is None:
            init_logger_from_configuration(configuration_file_full_path)
            StaticData.configuration_file_full_path = configuration_file_full_path
        elif StaticData.configuration_file_full_path != configuration_file_full_path:
            raise ValueError(
                f"Reconfiguring logger is not supported: Previous: {StaticData.configuration_file_full_path}, "
                f"received: {configuration_file_full_path}")

    return StaticData.logger


def get_raw_logger(name, format_string="%(message)s"):
    """
    Reuse logger
    :return:
    """

    try:
        return StaticData.raw_loggers[name]
    except KeyError:
        handler_tmp = logging.StreamHandler()
        formatter_tmp = logging.Formatter(
            format_string
        )
        handler_tmp.setFormatter(formatter_tmp)
        logger_tmp = logging.getLogger(name)
        logger_tmp.setLevel("INFO")
        logger_tmp.addHandler(handler_tmp)
        StaticData.raw_loggers[name] = logger_tmp

    return StaticData.raw_loggers[name]
