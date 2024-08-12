"""
Entry point for the receiver lambda.

"""

import json
import traceback

from horey.alert_system.lambda_package.event_handler import EventHandler
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy

from horey.h_logger import get_logger
logger = get_logger()


def lambda_handler(event, _):
    """
    Entry point for this lambda

    :param event:
    :param _: context
    :return:
    """

    logger_string = json.dumps(event).replace(AlertSystemConfigurationPolicy.ALERT_SYSTEM_SELF_MONITORING_LOG_FILTER_PATTERN,
                                          "ALERT_SYSTEM_SELF_MONITORING_LOG_FILTER_PATTERN")
    logger.info(f"Handling event: '{logger_string}'")

    event_handler = EventHandler(AlertSystemConfigurationPolicy.ALERT_SYSTEM_CONFIGURATION_FILE_PATH)
    try:
        event_handler.handle_event(event)
    except Exception as error_inst:
        traceback_str = "".join(traceback.format_tb(error_inst.__traceback__))
        return {"statusCode": 404, "body": json.dumps({"repr": repr(error_inst), "traceback": traceback_str})}

    return {"statusCode": 200, "body": json.dumps("Hello from Alert System 2!")}
