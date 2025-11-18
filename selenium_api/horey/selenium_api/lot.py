import copy


class Lot:
    def __init__(self):
        self.id = None
        self.auction_event_id = None
        self.name = None
        self.description = None
        self.interested = None
        self.current_max = None
        self.starting_bid = None
        self.my_max = None
        self.admin_fee = None
        self.raw_text = None
        self.url = None
        self.image_url = None
        self.address = None
        self.province = None

    def generate_ai_min_price_prompt(self):
        """
        Generate prompt

        :return:
        """

        return f"What is the minimal price in Canada Manitoba for the following item. Return only integer indicating the price, or string 'None' if you can not find this information. I" \
               f"Auction item image- '{self.image_url}', Auction item start description- '{self.description}' Auction item end description."

    def generate_db_tuple(self):
        """
        Dict to be pushed to DB.

        :return:
        """

        if not self.auction_event_id:
            breakpoint()
            raise RuntimeError("Auction_event_id can not be empty")
        if not self.address:
            breakpoint()
            raise RuntimeError("Address can not be empty")

        if not self.province:
            breakpoint()
            raise RuntimeError("Province can not be empty")

        if self.interested is None:
            breakpoint()
            raise RuntimeError("Interested can not be empty")

        ret = copy.deepcopy(self.__dict__)
        for attr in ["id"]:
            del ret[attr]

        return (
            ret["auction_event_id"],
            ret["name"],
            ret["description"],
            ret["interested"],
            ret["starting_bid"],
            ret["current_max"],
            ret["my_max"],
            ret["admin_fee"],
            ret["raw_text"],
            ret["url"],
            ret["image_url"],
            ret["address"],
            ret["province"],
        )

    def init_from_db_line(self, line):
        """
        Standard.

        :param line:
        :return:
        """

        self.id = line[0]
        self.auction_event_id = line[1]
        self.name = line[2]
        self.description = line[3]
        self.interested = line[4] != 0
        self.starting_bid = line[5]
        self.current_max = line[6]
        self.my_max = line[7]
        self.admin_fee = line[8]
        self.raw_text = line[9]
        self.url = line[10]
        self.image_url = line[11]
        self.address = line[12]
        self.province = line[13]

    def init_province_description_and_interested(self, str_auction_event_provinces):
        """
        Based address

        :return:
        """

        if self.province is None:
            auction_event_province = None

            if str_auction_event_provinces:
                auction_event_provinces = str_auction_event_provinces.split(",")
                if len(auction_event_provinces) == 1:
                    auction_event_province = auction_event_provinces[0]

            provinces = self.guess_provinces(self.address.lower())
            if len(provinces) > 1:
                raise NotImplementedError(f"Expected single province got {provinces} from: '{self.name}'")
            elif len(provinces) == 1:
                self.province = provinces[0]
            elif auction_event_province:
                self.province = auction_event_province
            else:
                # lot.province = "new brunswick"
                breakpoint()
                print(f"Manually set provinces for {self.url}")
                print(self.url)

        if self.interested is None:
            self.interested = self.province == "manitoba"

        if self.description is None:
            self.description = self.raw_text or self.name

    @staticmethod
    def guess_provinces(str_src):
        """
        Guess the province

        :param str_src:
        :return:
        """
        str_src = str_src.lower()

        ret = []
        known_locations = {"winnipeg": "manitoba",
                           "brunswick": "new brunswick",
                           "fredericton": "new brunswick",
                           "calgary": "alberta",
                           "edmonton": "alberta",
                           **{province: province for province in
                              ["offsite", "manitoba", "alberta", "new brunswick"]}}

        for location, province in known_locations.items():
            if location not in str_src:
                continue
            ret.append(province)

        return list(set(ret))
