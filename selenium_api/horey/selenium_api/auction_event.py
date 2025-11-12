import datetime
import json

from horey.common_utils.common_utils import CommonUtils
from horey.selenium_api.lot import Lot


class AuctionEvent:
    selenium_api = None

    def __init__(self):
        self.id = None
        self.provider_id = None
        self.name = None
        self.url = None
        self.start_time = None
        self.end_time = None
        self.address = ""
        self.provinces = ""
        self.description = None
        self.lots = []
        self.last_update_time = None

    @property
    def finished(self):
        return self.end_time < datetime.datetime.now(tz=datetime.timezone.utc)

    def generate_db_tuple(self):
        """
        Dict to be pushed to DB.
        def init_from_dict(obj_dst, dict_src, custom_types=None):

        :return:
        """

        if not self.provinces:
            self.init_provinces()

            if not self.provinces:
                # self.provinces = "new brunswick"
                breakpoint()
                print(f"Manually set provinces for {self.url}")
                print(self.url)

        ret = CommonUtils.convert_to_dict(self.__dict__)

        for attr in ["lots", "id", "provider_id"]:
            del ret[attr]

        for field in ["start_time", "end_time", "last_update_time"]:
            ret[field] = json.dumps(ret[field])

        return (
            ret["name"],
            ret["description"],
            ret["url"],
            ret["start_time"],
            ret["end_time"],
            ret["address"],
            ret["provinces"],
            ret["last_update_time"]
        )

    def init_provinces(self):
        """
        Init provinces string

        :return:
        """

        provinces = Lot.guess_provinces(self.name.lower())
        if self.address:
            provinces += Lot.guess_provinces(self.address.lower())
        if self.description:
            provinces += Lot.guess_provinces(self.description.lower())

        self.provinces = ",".join(set(provinces))

    def init_from_db_line(self, line):
        """
        Standard.

        :param line:
        :return:
        """

        self.id = line[0]
        self.provider_id = line[1]
        self.name = line[2]
        self.description = line[3]
        self.url = line[4]
        CommonUtils.init_from_dict(self, {"start_time": json.loads(line[5])})
        CommonUtils.init_from_dict(self, {"end_time": json.loads(line[6])})
        self.address = line[7]
        self.provinces = line[8]

        if line[9]:
            CommonUtils.init_from_dict(self, {"last_update_time": json.loads(line[9])})

    def init_lots_default_information(self):
        """
        Init default lots default values.

        :return:
        """

        for lot in self.lots:
            lot.init_province_description_and_interested(self.provinces)
            if not lot.province:
                raise RuntimeError("Was not able to init")
            if lot.current_max is None:
                breakpoint()

    def print_interesting_information(self):
        """
        Magic

        :return:
        """

        str_ret = f"Auction {self.url} ending time: {self.end_time}"
        # todo: fix. Find why there are nones
        lots = [lot for lot in self.lots if lot.current_max is not None]

        lots = [lot for lot in lots if lot.interested]

        lots = sorted(lots, key=lambda lot: lot.current_max)
        for lot in lots:
            if not lot.interested:
                continue
            str_ret += f"\n{lot.current_max}$, {lot.name}, {lot.url}"
        str_ret += f"\n Auction {self.id} END"
        print(str_ret)

