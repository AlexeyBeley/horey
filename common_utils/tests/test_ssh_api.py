"""
SSH API tests

"""

import os

from horey.common_utils.ssh_api import SSHAPI

# pylint: disable= missing-function-docstring


def test_generate_ed25519_key():
    self_dir_path = os.path.dirname(os.path.abspath(__file__))
    SSHAPI.generate_ed25519_key("horey_horey@gmail.com", self_dir_path)


if __name__ == "__main__":
    test_generate_ed25519_key()
