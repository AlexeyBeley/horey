
class FreeItem:
    def __init__(self, name, url, image_url=None, description=None, address=None):
        self.name = name
        self.url = url
        self.image_url = image_url
        self.description = description
        self.address = address


    def generate_message(self):
        return f"(Free)\n [{self.name}]\n<a href=\"{self.url}\">Link to the message</a>\n{self.description}"

    def generate_db_tuple(self):
        """
        Generate insertion tuple for db.

        :return:
        """

        return (self.name, self.description, self.url, self.image_url, self.address)
