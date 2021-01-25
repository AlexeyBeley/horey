
import sys
import os
import pdb
import datetime
from unittest.mock import Mock, patch
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "horey", "common_utils"))

from actions_manager import ActionsManager

def test_call_action_do_not_pass_unknown_args():
    actions_manager = ActionsManager()
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, type=str, help="Object type to init")
    action_function = Mock()

    actions_manager.register_action("test_action", lambda: parser, action_function)

    testargs = ["asd", "--action", "test_action", "--target", "target_test"]
    with patch("sys.argv", testargs):
       actions_manager.call_action()

    action_function.assert_called_once()


def test_call_action_pass_unknown_args():
    actions_manager = ActionsManager()
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, type=str, help="Object type to init")
    action_function = Mock()

    actions_manager.register_action("test_action", lambda: parser, action_function)

    testargs = ["asd", "--action", "test_action", "--target", "target_test", "--region", "us-east-1", "--configuration_file_name", "test.json"]
    with patch("sys.argv", testargs):
       actions_manager.call_action(pass_unknown_args=True)

    action_function.assert_called_with(parser.parse_args(["--target", "target_test"]), {'region': 'us-east-1', 'configuration_file_name': 'test.json'})


test_call_action_pass_unknown_args()