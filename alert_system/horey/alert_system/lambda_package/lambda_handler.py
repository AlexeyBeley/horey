"""
Entry point for the receiver lambda.

"""

import json
import traceback

from event_handler import EventHandler

from horey.h_logger import get_logger
logger = get_logger()


def lambda_handler(event, _):
    """
    Entry point for this lambda

    :param event:
    :param _: context
    :return:
    """
    logger_string = json.dumps(event)
    if "log_group_filter_pattern" in logger_string:
        try:
            filter_string_start_index = logger_string.index("log_group_filter_pattern")
            filter_string_start_index = (
                logger_string.index(r": \\\"", filter_string_start_index) + 6
            )
            filter_string_end_index = logger_string.index(
                r"\\\"}, \\\"type\\\":", filter_string_start_index
            )
            logger_string = (
                logger_string[:filter_string_start_index]
                + "filter_string_removed_to_exclude_recursion"
                + logger_string[filter_string_end_index:]
            )
        except Exception as error_inst:
            traceback_str = "".join(traceback.format_tb(error_inst.__traceback__))
            logger.exception(f"{traceback_str}\n{repr(error_inst)}")

    logger.info(f"Handling event: '{logger_string}'")

    event_handler = EventHandler(logger)
    event_handler.handle_event(event)
    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
