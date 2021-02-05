import os
import sys
from pytest import raises


sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "configuration_policies"))


from grade_configuration_policy import GradeConfigurationPolicy


def test_init():
    assert isinstance(GradeConfigurationPolicy(), GradeConfigurationPolicy)


def test_leverage_grade():
    config = GradeConfigurationPolicy()
    config.grade = "STG"
    config.grade = "PROD"


def test_wrong_leverage_grade():
    config = GradeConfigurationPolicy()
    config.grade = "STG"
    with raises(ValueError):
        config.grade = "QA"


def test_init_from_json_file():
    file_path = "configuration_values/grade_configuration_prod_with_name.json"
    config_values = {
        "configuration_file_full_path": file_path}

    config = GradeConfigurationPolicy()
    config.init_from_dictionary(config_values)
    config.init_from_json_file()
