import json
import os
import sys
import pdb

sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(0, "/Users/alexeybe/private/IP/ip")
sys.path.insert(0, "/Users/alexeybe/private/aws_api/ignore")
sys.path.insert(0, "/Users/alexeybe/private/aws_api/src/base_entities")

from terraform_parser import TerraformParser
import ignore_me
import logging
logger = logging.Logger(__name__)
from aws_account import AWSAccount

tested_account = ignore_me.acc_prod_eu

AWSAccount.set_aws_account(tested_account)

terraform_parser = TerraformParser("/Users/alexeybe/private/aws_api/ignore/prod_eu_tf_state.json")


def test_parse_to_objects():
    terraform_parser.parse_to_objects()

test_parse_to_objects()