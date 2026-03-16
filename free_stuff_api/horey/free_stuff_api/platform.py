
class Platform:
    def __init__(self, _id, name, api=None):
        self.name = name
        self.api = api
        self.id = _id
        self.free_items = None
