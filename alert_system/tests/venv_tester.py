"""
Test locally lambda package.

"""

import os
import json

import sys
from lambda_handler import lambda_handler

os.environ["ALERT_SYSTEM_NOTIFICATION_CHANNELS"] = "notification_channel_slack.py"
os.chdir(os.path.dirname(os.path.abspath(__file__)))
with open(
    sys.argv[1],
    encoding="utf-8",
) as fh:
    ret = json.load(fh)


#with open(
#    os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_event.json"),
#    encoding="utf-8",
#) as fh:
#    ret = json.load(fh)

lambda_handler(ret, None)
