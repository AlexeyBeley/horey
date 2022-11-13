import json
import pdb

from horey.alert_system.lambda_package.message import Message
import os
from horey.common_utils.common_utils import CommonUtils

mock_values_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


def test_init_message_receiver():
    assert isinstance(Message({}), Message)


def test_convert_to_dict():
    message = Message({"dict_src": "dict_src"})
    message.type = "TEST_MESSAGE"
    message.data = json.dumps({"key": "value"})
    message.generate_uuid()
    ret = message.convert_to_dict()
    ret["uuid"] = "62fe1fa6-d5a4-4c22-b523-d85e82a44954"
    assert ret == {
        "dict_src": {"dict_src": "dict_src"},
        "uuid": "62fe1fa6-d5a4-4c22-b523-d85e82a44954",
        "data": '{"key": "value"}',
        "type": "TEST_MESSAGE",
    }


def test_init_from_dict():
    message = Message({"dict_src": "dict_src"})
    message.init_from_dict(
        {
            "dict_src": {"dict_src": "dict_src"},
            "uuid": "62fe1fa6-d5a4-4c22-b523-d85e82a44954",
            "data": '{"key": "value"}',
            "type": "TEST_MESSAGE",
        }
    )
    assert message.type == "TEST_MESSAGE"


if __name__ == "__main__":
    test_convert_to_dict()
    test_init_from_dict()
