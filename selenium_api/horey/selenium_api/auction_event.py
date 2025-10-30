import json

from horey.common_utils.common_utils import CommonUtils

class AuctionEvent:
    selenium_api = None

    def __init__(self):
        self.id = None
        self.provider_id = None
        self.name = None
        self.link = None
        self.start_time = None
        self.end_time = None
        self.address = ""
        self.provinces = ""
        self.description = None
        self.lots = []

    def generate_db_tuple(self):
        """
        Dict to be pushed to DB.
        def init_from_dict(obj_dst, dict_src, custom_types=None):

        :return:
        """

        if not self.provinces:
            lower_name = self.name.lower()
            self.provinces = ""

            for province in ["manitoba", "alberta", "new brunswick", "calgary"]:
                if province in lower_name:
                    if self.provinces:
                        self.provinces += f",{province}"
                    else:
                        self.provinces = province
            if not self.provinces:
                print(self.link)
                # self.provinces = "new brunswick"
                breakpoint()

        ret = CommonUtils.convert_to_dict(self.__dict__)

        for attr in ["lots", "id", "provider_id"]:
            del ret[attr]

        for field in ["start_time", "end_time"]:
            ret[field] = json.dumps(ret[field])

        return (
            ret["name"],
            ret["description"],
            ret["link"],
            ret["start_time"],
            ret["end_time"],
            ret["address"],
            ret["provinces"]
        )

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
        self.link = line[4]
        CommonUtils.init_from_dict(self, {"start_time": json.loads(line[5])})
        CommonUtils.init_from_dict(self, {"end_time": json.loads(line[6])})
        self.address = line[7]
        self.provinces = line[8]
