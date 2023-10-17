"""
Testing replacement_engine

"""

import os
import json
import pytest

from horey.replacement_engine.replacement_engine import ReplacementEngine

# pylint: disable=missing-function-docstring

@pytest.mark.done
def test_perform_raw_cartesian_replacements():
    str_src = json.dumps({"1": [[{1:["1", "STRING_REPLACEMENT_X_test"]}], ["STRING_REPLACEMENT_Y"]]})
    string_to_list_replacements = {"STRING_REPLACEMENT_X": ["1", "2"],
                                   "STRING_REPLACEMENT_Y": ["3", "4", "5"]}
    ret = ReplacementEngine.perform_raw_cartesian_replacements(str_src, string_to_list_replacements)
    assert json.loads(ret) == {"1": [[{"1": ["1", "1_test", "2_test"]}], ["3", "4", "5"]]}


@pytest.fixture(name="file_path")
def fixture_file_path():
    """
    Fixture used as a base config.

    :return:
    """

    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template_STRING_REPLACEMENT_0.json")
    obj = {"STRING_REPLACEMENT_1": ["STRING_REPLACEMENT_2"]}
    with open(file_path, "w", encoding="utf-8") as file_handler:
        json.dump(obj, file_handler)
    yield file_path
    os.remove(file_path)

@pytest.mark.done
def test_perform_file_string_replacements(file_path):
    ReplacementEngine.perform_file_string_replacements(os.path.dirname(file_path), os.path.basename(file_path),
                                                             {"STRING_REPLACEMENT_0": "tmp",
                                                                 "STRING_REPLACEMENT_1": "1"},
                                                             cartesian_replacements={"STRING_REPLACEMENT_2": ["2", "3"]})
    with open(os.path.join(os.path.dirname(file_path), "tmp.json"), encoding="utf-8") as file_handler:
        response = json.load(file_handler)
    assert response == {"1": ["2", "3"]}
