import json
import os
import pdb

from horey.alert_system.lambda_package.lambda_handler import lambda_handler

with open("./clowdwatch_messages/sqs_alert.json") as file_handler:
    event = json.load(file_handler)

os.environ["SLACK_API_CONFIGURATION_FILE"] = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                 "slack_api_configuration_values.py"))

lambda_handler(event, None)
