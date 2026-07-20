"""
Running tests of several jenkins_api possibilities.
Not really tests but more like a usage demonstration.
"""
import sys
from pathlib import Path
from unittest.mock import patch


import pytest

from horey.jenkins_api.jenkins_api_actor import run_job_from_env_vars, action_manager


@pytest.mark.done
def test_run_job_from_env_vars():
    """
    Test basic init.

    @return:
    """

    class Arguments:
        job_name = "job_name"
        jenkins_api_config_file = str(Path(__file__).parent.absolute() / "jenkins_api_configuration_values.py")
        var1 = "var1"
        var2 = "var2"
        var3 = "var3"
        var4 = "var4"

    assert run_job_from_env_vars(Arguments)


jenkins_api_config_file = str(Path(__file__).parent.absolute() / "jenkins_api_configuration_values.py")


@pytest.mark.done
@patch.object(sys, 'argv', ['script.py', '--job_name', 'test-job', '--action', 'run_job_from_env_vars', "--jenkins_api_config_file", jenkins_api_config_file, "--arg1", "arg1"])
def test_run_job_from_env_vars_from_action_manager():
    """
    Test basic init.

    @return:
    """

    assert action_manager.call_action(pass_unknown_args=True)

