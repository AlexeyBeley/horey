"""
Pip api configuration

"""
import os


class ConfigValues:
    """
    Main class.

    """

    def __init__(self):
        tests_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.multi_package_repositories = {"horey.":
            os.path.dirname(os.path.dirname(tests_dir))
        }
        self.venv_dir_path = os.path.join(
            tests_dir, "venv"
        )


def main():
    """
    Main class

    :return:
    """

    return ConfigValues()
