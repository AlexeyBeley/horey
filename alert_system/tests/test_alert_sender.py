import pdb

from horey.docker_api.docker_api import DockerAPI
import os
from horey.common_utils.common_utils import CommonUtils
from horey.aws_api.aws_api import AWSAPI

mock_values_file_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ignore", "mock_values.py"))
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


def test_init_docker_api():
    assert isinstance(DockerAPI(), DockerAPI)


def test_send_message():
    docker_api = DockerAPI()
    aws_api = AWSAPI()
    docker_api.login(registry, username, password)



if __name__ == "__main__":
    test_send_message()
