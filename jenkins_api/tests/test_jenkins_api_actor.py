"""
Running tests of several jenkins_api possibilities.
Not really tests but more like a usage demonstration.
"""
from pathlib import Path

import pytest

from horey.jenkins_api.jenkins_api_actor import run_job_from_env_vars


@pytest.mark.wip
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
