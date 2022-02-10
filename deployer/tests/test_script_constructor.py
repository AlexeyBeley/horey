import os
import sys
import pdb
from unittest import mock
import pytest
from shutil import copyfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
from horey.deployer.script_constructor import ScriptConstructor


def test_init_script_file():
    data_level_0_dir = os.path.join(TESTS_DIR, "data_dir0")
    os.makedirs(data_level_0_dir, exist_ok=True)
    script_path = os.path.join(data_level_0_dir, "script.sh")
    os.remove(script_path)
    constructor = ScriptConstructor(script_path)

    assert isinstance(constructor, ScriptConstructor)
    assert os.path.exists(script_path)


def test_add_module():
    data_level_0_dir = os.path.join(TESTS_DIR, "data_dir0")
    os.makedirs(data_level_0_dir, exist_ok=True)
    script_path = os.path.join(data_level_0_dir, "script.sh")
    os.remove(script_path)
    constructor = ScriptConstructor(script_path)
    constructor.add_module(os.path.join(TESTS_DIR, "deployment_scripts_1", "test_script_1.sh"))
    assert isinstance(constructor, ScriptConstructor)


def test_add_modules():
    data_level_0_dir = os.path.join(TESTS_DIR, "data_dir0")
    os.makedirs(data_level_0_dir, exist_ok=True)
    script_path = os.path.join(data_level_0_dir, "script.sh")
    os.remove(script_path)
    constructor = ScriptConstructor(script_path)
    constructor.add_module(os.path.join(TESTS_DIR, "deployment_scripts_1", "test_script_1.sh"))
    constructor.add_module(os.path.join(TESTS_DIR, "deployment_scripts_1", "deployment_scripts_2", "test_script_2.sh"))

    constructor.add_module(os.path.join(TESTS_DIR, "deployment_scripts_1", "test_script_3.sh"),
                           put_near_script_file=True)

    assert isinstance(constructor, ScriptConstructor)


if __name__ == "__main__":
    #test_init_script_file()
    #test_add_module()
    test_add_modules()

