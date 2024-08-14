"""
Used to as entrypoint script to trigger lambda locally.

"""

import json
import os
os.chdir(os.path.abspath(os.path.dirname(__file__)))

from lambda_handler import lambda_handler

with open("event.json", encoding="utf-8") as file_handler:
    event = json.load(file_handler)

ret = lambda_handler(event, None)

with open("result.json", "w", encoding="utf-8") as file_handler:
    json.dump(ret, file_handler)
