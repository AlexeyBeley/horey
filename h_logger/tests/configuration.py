"""
Sample configs
"""
import os


def main():
    """
    Configs fetcher

    :return:
    """

    output_dir = os.path.join(os.path.dirname(__file__), "output")

    class Tmp:
        """
        Configs Aggregator.

        """

        def __init__(self):
            self.error_level_file_path = os.path.join(output_dir, "error.log")
            self.info_level_file_path = os.path.join(output_dir, "info.log")

    return Tmp()
