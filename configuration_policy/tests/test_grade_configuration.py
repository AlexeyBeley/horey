import os
import sys
from pytest import raises
import pytest
import pdb

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "configuration_policies"))


from grade_configuration_policy import GradeConfigurationPolicy


configuration_values_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "configuration_values")


def test_init():
    assert isinstance(GradeConfigurationPolicy(), GradeConfigurationPolicy)


@pytest.fixture
def configuration_policy():
    configuration_policy = GradeConfigurationPolicy()
    configuration_policy.grade = "STG"
    return configuration_policy


def test_increasing_stg_grade_to_prod(configuration_policy):
    configuration_policy.grade = GradeConfigurationPolicy.GradeValue.PROD.name
    assert configuration_policy.grade == GradeConfigurationPolicy.GradeValue.PROD.name


def test_raising_decreasing_stg_grade_to_qa(configuration_policy):
    with raises(ValueError):
        configuration_policy.grade = GradeConfigurationPolicy.GradeValue.QA.name


def test_init_from_json_file():
    file_path = os.path.join(configuration_values_dir, "grade_configuration_prod_with_name.json")
    config_values = {"configuration_file_full_path": file_path}

    config = GradeConfigurationPolicy()
    config.init_from_dictionary(config_values)
    config.init_from_json_file()
