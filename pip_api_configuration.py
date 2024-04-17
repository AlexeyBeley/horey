"""
Pip api configuration

"""
import os


class ConfigValues:
    """
    Main class.

    """

    def __init__(self):
        horey_dir = os.path.dirname(os.path.abspath(__file__))
        self.multi_package_repositories = {"horey.": horey_dir
        }
        self.venv_dir_path = os.path.join(
            horey_dir, "build", "_build", "_venv"
        )


def main():
    """
    Main class

    :return:
    """

    return ConfigValues()
