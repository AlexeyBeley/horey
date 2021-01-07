import os
import sys
from unittest import mock
import argparse
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "configuration_files"))

from grade_configuration import GradeConfiguration


def test_init():
    assert isinstance(GradeConfiguration(), GradeConfiguration)


def test_leverage_grade():
    config = GradeConfiguration()
    config.grade = "STG"
    config.grade = "PROD"


@pytest.mark.skip(reason="No way of currently testing this")
def test_wrong_leverage_grade():
    config = GradeConfiguration()
    config.grade = "STG"
    config.grade = "QA"


