"""
Message dispatcher tests.

"""
import os
import shutil

import pytest
from horey.common_utils.common_utils import CommonUtils

# pylint: disable= missing-function-docstring


@pytest.fixture(name="lambda_package_tmp_dir")
def fixture_lambda_package_tmp_dir_message_dispatcher():
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "horey", "alert_system", "lambda_package"))
    dst_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "lambda_package"))

    shutil.copytree(src_dir, dst_dir)
    shutil.copy2(os.path.join(os.path.dirname(__file__), "notification_channel_ses_configuration_values.py"), dst_dir)
    yield dst_dir
    shutil.rmtree(dst_dir)


@pytest.mark.wip
def test_init_message_dispatcher(lambda_package_tmp_dir):
    message_dispatcher_base_file_path = os.path.join(lambda_package_tmp_dir, "message_dispatcher_base.py")
    message_dispatcher_base = CommonUtils.load_object_from_module_raw(message_dispatcher_base_file_path, "MessageDispatcherBase")
    assert message_dispatcher_base.__name__ == "MessageDispatcherBase"
