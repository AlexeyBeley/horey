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
        self.multi_package_repositories = [
            os.path.dirname(os.path.dirname(tests_dir))
        ]


def main():
    """
    Main class

    :return:
    """

    return ConfigValues()
