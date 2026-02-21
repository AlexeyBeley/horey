
class FreeItem:
    def __init__(self, name, url, image_url=None, description=None):
        self.name = name
        self.url = url
        self.image_url = image_url
        self.description = description


    def generate_message(self):
        return f"(Free)\n [{self.name}]\n<a href=\"{self.url}\">Link to the message</a>\n{self.description}"
