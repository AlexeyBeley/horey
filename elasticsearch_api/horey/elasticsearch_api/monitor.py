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
        for key in ["id", "name", "inputs", "enabled", "schedule", "triggers"]:
            ret[key] = getattr(self, key)

        return ret

    def init_from_dict(self, dict_src):
        for key, value in dict_src.items():
            setattr(self, key, value)

    def generate_create_request(self):
        request = {
            "type": "monitor",
            "name": self.name,
            "monitor_type": "query_level_monitor",
            "enabled": True,
            "schedule": self.schedule,
            "inputs": self.inputs,
            "triggers": self.triggers,
        }
        return request
