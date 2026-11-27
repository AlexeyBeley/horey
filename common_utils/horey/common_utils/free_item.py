
class FreeItem:
    def __init__(self, name, url, image_url=None, description=None, address=None, ingestion_time=None, _id=None):
        self.id = _id
        self.name = name
        self.url = url
        self.image_url = image_url
        self.description = description
        self.address = address
        self.ingestion_time = ingestion_time


    def generate_message(self):
        return (f"(Free)\n "
                f"[{self.name}]\n"
                f"{self.description}\n"
                f"<a href=\"{self.url}\">Link to the message</a>"
                f"<a href=\"{self.image_url}\">.</a>"
                )

    def generate_db_tuple(self):
        """
        Generate insertion tuple for db.

        :return:
        """

        return (self.name, self.description, self.url, self.image_url, self.address)

    def print(self):
        """
        Print the data
        :return:
        """

        str_ret = (f"Name: {self.name}\n"
                   f"Description: {self.description}")
        print(str_ret)
        return str_ret
