"""
Entry point for the receiver lambda.

"""

import json
from pathlib import Path

from horey.free_stuff_api.free_stuff_api import FreeStuffAPI
from horey.free_stuff_api.free_stuff_api_configuration_policy import FreeStuffAPIConfigurationPolicy

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
    config = FreeStuffAPIConfigurationPolicy()
    config.init_from_file(file_path=Path(__file__).parent / "frs_api_configuration.json")
    hfrs_api = FreeStuffAPI(config)
    hfrs_api.main()


    # return {"statusCode": 404, "body": json.dumps({"repr": repr(error_inst), "traceback": traceback_str})}

    return {"statusCode": 200, "body": json.dumps("Hello from Horey FRee Stuff!")}

# handler(1,1)
