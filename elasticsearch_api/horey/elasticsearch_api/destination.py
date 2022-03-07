import pdb


class Destination:
    def __init__(self):
        self.dict_src = None
        self.id = None
        self.name = None
        self.type = None
        self.sns = None

    def init_from_search_reply(self, dict_src):
        self.dict_src = dict_src
        self.id = dict_src["id"]
        self.type = dict_src["type"]
        self.name = dict_src["name"]
        self.sns = dict_src["sns"]

    def convert_to_dict(self):
        ret = {}
        for key in ["id",
                    "name",
                    "type",
                    "sns"]:
            ret[key] = getattr(self, key)

        return ret
