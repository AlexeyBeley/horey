"""
AWS region metadata
"""


class Region:
    """
    AWS Region class
    """
    REGIONS = {}

    @staticmethod
    def get_region(region_mark):
        try:
            return Region.REGIONS[region_mark]
        except KeyError:
            Region.REGIONS[region_mark] = Region()
            Region.REGIONS[region_mark].region_mark = region_mark

        return Region.REGIONS[region_mark]

    def __init__(self):
        self._region_mark = None
        self._region_name = None

    def __str__(self):
        return self.region_mark

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

    def convert_to_dict(self):
        return {"region_mark": self._region_mark, "region_name": self._region_name}

    def init_from_dict(self, dict_src):
        for attr, value in dict_src.items():
            setattr(self, attr, value)
