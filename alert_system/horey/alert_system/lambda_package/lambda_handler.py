"""
Entry point for the receiver lambda.

"""
import copy
import json
import traceback

from horey.alert_system.lambda_package.event_handler import EventHandler

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
            dict_message = json.loads(event["Records"][0]["Sns"]["Message"])
            alarm_description = json.loads(dict_message["AlarmDescription"])
            pattern = alarm_description["log_group_filter_pattern"]
            pattern_middle = int(len(pattern) // 2)
            pattern = pattern[:pattern_middle] + "_horey_explicit_split_" + pattern[pattern_middle:]
            alarm_description["log_group_filter_pattern"] = pattern
            dict_message["AlarmDescription"] = json.dumps(alarm_description)
            event_copy = copy.deepcopy(event)
            event_copy["Records"][0]["Sns"]["Message"] = json.dumps(dict_message)
            logger_string = json.dumps(event_copy)
        except Exception as error_inst:
            traceback_str = "".join(traceback.format_tb(error_inst.__traceback__))
            logger.exception(f"{traceback_str}\n{repr(error_inst)}")

    logger.info(f"Handling event: '{logger_string}'")

    event_handler = EventHandler()
    try:
        event_handler.handle_event(event)
    except Exception as error_inst:
        traceback_str = "".join(traceback.format_tb(error_inst.__traceback__))
        return {"statusCode": 404, "body": json.dumps({"repr": repr(error_inst), "traceback": traceback_str})}

    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
