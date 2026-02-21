"""
Entry point for the receiver lambda.

"""

import json

from horey.free_stuff_api.free_stuff_api import FreeStuffAPI

from horey.h_logger import get_logger
logger = get_logger()


def handler(event, _):
    """
    Entry point for this lambda

    :param event:
    :param _: context
    :return:
    """

    logger_string = json.dumps(event)
    logger.info(f"Handling event: '{logger_string}'")
    fb_api = FreeStuffAPI()
    fb_api.load_free_logged_out()


    # return {"statusCode": 404, "body": json.dumps({"repr": repr(error_inst), "traceback": traceback_str})}

    return {"statusCode": 200, "body": json.dumps("Hello from Alert System 2!")}
