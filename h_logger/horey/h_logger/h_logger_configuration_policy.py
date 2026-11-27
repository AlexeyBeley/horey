"""
Logger configuration

"""


# pylint: disable = missing-function-docstring


class HLoggerConfigurationPolicy:
    """
    Main Class
    """

    def __init__(self):
        super().__init__()
        self._error_level_file_path = None
        self._info_level_file_path = None

    @property
    def info_level_file_path(self):
        return self._info_level_file_path

    @info_level_file_path.setter
    def info_level_file_path(self, value):
        self._info_level_file_path = value

    @property
    def error_level_file_path(self):
        return self._error_level_file_path

    @error_level_file_path.setter
    def error_level_file_path(self, value):
        self._error_level_file_path = value
