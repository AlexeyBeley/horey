import os
import pdb
import json
from lambda_handler import lambda_handler

os.environ["SLACK_API_CONFIGURATION_FILE"] = "slack_api_configuration_file.py"

with open(os.path.join(os.path.dirname(os.path.abspath(__file__))), "alert_system_self_alert_event.json") as fh:
    ret = json.load(fh)

lambda_handler(ret, None)
