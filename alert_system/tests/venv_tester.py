"""
Test locally lambda package.

"""

import os
import json
from lambda_handler import lambda_handler

os.environ["ALERT_SYSTEM_NOTIFICATION_CHANNELS"] = "notification_channel_slack.py"

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_event.json"), encoding="utf-8") as fh:
    ret = json.load(fh)

lambda_handler(ret, None)
