import json
import pdb


class TerraformParser:
    def __init__(self, path):
        with open(path) as file_handler:
            self.dict_src = json.load(file_handler)

    def parse_to_objects(self):
        # pdb.set_trace()
        for module in self.dict_src["modules"]:
            # print(list(module.keys()))
            print("@@@@@@@@@@@@@@@@@@@@@@")
            print(module.get("path"))
            print(module.get("outputs"))
            print(module.get("resources"))
            print(module.get("depends_on"))

        pdb.set_trace()
