"""
Testing github api functionality.

"""

import json
from pathlib import Path
import pytest
from horey.github_api.actions.job import Job

# pylint: disable = missing-function-docstring

@pytest.mark.unit
def test_init_from_file():
    with open(Path(__file__).parent / "jobs"/ "worflow_run_job_api.json", encoding="utf-8") as fh:
        dict_src = json.load(fh)
        assert Job("test").init_from_dict(dict_src)
