"""
AWS region metadata
"""


class Region:
    """
    AWS Region class
    """

    def __init__(self):
        self._region_mark = None
        self._region_name = None
        self.connection_steps = []

    @property
    def region_mark(self):
        """
        Standard aws mark getter e.g. us-east-1
        :return:
        """
        return self._region_mark

    @region_mark.setter
    def region_mark(self, value):
        """
        Standard aws mark setter e.g. us-east-1
        :return:
        """
        self._region_mark = value

    @property
    def region_name(self):
        """
        AWS region name getter - user friendly
        :return:
        """
        return self._region_name

    @region_name.setter
    def region_name(self, value):
        """
        AWS region name setter - user friendly
        :return:
        """
        self._region_name = value
