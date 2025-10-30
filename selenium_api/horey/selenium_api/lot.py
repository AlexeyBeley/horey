
class Lot:
    def __init__(self):
        self.high_bid = None
        self.image_url = None
        self.url = None
        self.name = None
        self.description = None

    def generate_ai_min_price_prompt(self):
        """
        Generate prompt

        :return:
        """

        return f"What is the minimal price in Canada Manitoba for the following item. Return only integer indicating the price, or string 'None' if you can not find this information. I" \
               f"Auction item image- '{self.image_url}', Auction item start description- '{self.description}' Auction item end description."

