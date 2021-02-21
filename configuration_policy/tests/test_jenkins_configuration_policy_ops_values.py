import os
import sys
from unittest import mock
import argparse


sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "configuration_policies"))

from jenkins_deploy_configuration import JenkinsDeployConfiguration


def test_init():
    assert isinstance(JenkinsDeployConfiguration(), JenkinsDeployConfiguration)


def test_init_from_command_line():
    testargs = ["prog", "--output_file_name", "/home/fenton/project/setup.py"]
    description = "Fetch"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--output_file_name", required=False, type=str, default="aws_auth_info.json", help="Name of the output file")
    with mock.patch("sys.argv", testargs):
        config = Configuration()
        config.init_from_command_line(parser)

test_init()