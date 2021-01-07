import sys
import pdb
import argparse
import json

sys.path.insert(0, "/Users/alexeybe/private/aws_api/src")
sys.path.insert(0, "/Users/alexeybe/private/aws_api/ignore")

import ignore_me
from aws_api import AWSAPI
import logging
logger = logging.Logger(__name__)
from aws_account import AWSAccount

from actions_manager import ActionsManager

AWSAccount.set_aws_account(ignore_me.acc_default)
action_manager = ActionsManager()
aws_api = AWSAPI()


if __name__ == "__main__":
    action_manager.call_action()
