import pdb


class Monitor:
    def __init__(self):
        self.dict_src = None
        self.id = None
        self.name = None
        self.inputs = None
        self.enabled = None
        self.schedule = None
        self.triggers = None

    def init_from_search_reply(self, dict_src):
        self.dict_src = dict_src
        self.id = dict_src["_id"]
        self.name = dict_src["_source"]["name"]
        self.inputs = dict_src["_source"]["inputs"]
        self.enabled = dict_src["_source"]["enabled"]
        self.schedule = dict_src["_source"]["schedule"]
        self.triggers = dict_src["_source"]["triggers"]

    def convert_to_dict(self):
        ret = {}
        for key in ["id",
                    "name",
                    "inputs",
                    "enabled",
                    "schedule",
                    "triggers"]:
            ret[key] = getattr(self, key)

        return ret
