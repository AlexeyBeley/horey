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
        """
        Generate new region.
        :param region_mark:
        :return:
        """
        if not isinstance(region_mark, str):
            raise ValueError(
                f"Expecting region_mark of type string, received {type(region_mark)}"
            )
        try:
            return Region.REGIONS[region_mark]
        except KeyError:
            Region.REGIONS[region_mark] = Region()
            Region.REGIONS[region_mark].region_mark = region_mark

        return Region.REGIONS[region_mark]

    def __init__(self, dict_src=None, from_cache=None):
        self._region_mark = None
        self._region_name = None
        self.region_opt_status = None
        self.opt_in_status = None
        self.endpoint = None
        self.dict_src = dict_src

        if from_cache:
            for key, value in dict_src.items():
                setattr(self, key, value)
            return
        self.update_from_raw_response(dict_src)

    def __str__(self):
        return self.region_mark

    @staticmethod
    def get_cache_file_name():
        """
        Cache fetched regions.

        :return:
        """

        return "region.json"

    def update_from_raw_response(self, dict_src):
        """
        Standard.

        :param dict_src:
        :return:
        """
        if not dict_src:
            return

        keys = ["RegionOptStatus", "RegionName", "Endpoint", "OptInStatus"]

        for key, value in dict_src.items():
            if key not in keys:
                setattr(self, key, value)
            if key == "RegionOptStatus":
                self.region_opt_status = value
                continue
            if key == "RegionName":
                self.region_mark= value
                continue
            if key == "Endpoint":
                self.endpoint= value
                continue
            if key == "OptInStatus":
                self.opt_in_status = value
                continue

            raise NotImplementedError(key, value)

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
        """
        Serialize.

        :return:
        """
        return {**{key: value for key, value in self.__dict__.items() if not key.startswith("_")},
                 **{key[1:]: value for key, value in self.__dict__.items() if key.startswith("_")}}

    def init_from_dict(self, dict_src):
        """
        Deserialize.

        :param dict_src:
        :return:
        """

        for attr, value in dict_src.items():
            setattr(self, attr, value)
