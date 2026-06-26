
class Platform:
    def __init__(self, _id, name, api=None):
        self.name = name
        self.api = api
        self.id = _id
        self.free_items = None


    def get_new_free_items(self):
        """
        Get new items from platform

        :return:
        """

        current_free_items = self.api.get_free_items()
        known_descriptions = [free_item.description for free_item in self.free_items]
        breakpoint()
        return [current_free_item for current_free_item in current_free_items if current_free_item.description not in known_descriptions]
