"""
Pip api configuration
"""
import os


class ConfigValues:
    """
    Main class.

    """

    def __init__(self):
        self.multi_package_repositories = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../")
        ]
        self.venv_dir_path = os.path.join(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "test_venv")
        )


def main():
    """
    Main class

    :return:
    """

    return ConfigValues()
