"""
Price List is built from products and their prices.
This module manages single product data.

"""

# pylint: disable= missing-function-docstring
class PriceListProduct:
    """
    Pricing product.
    """

    def __init__(self, dict_src):
        self.dict_src = dict_src
        self.attributes = dict_src["attributes"]

    @property
    def cpu(self):
        return float(self.attributes["vcpu"])

    @property
    def ram(self):
        return self.attributes["memory"]

    @property
    def float_ram(self):
        if not self.ram.endswith("GiB"):
            raise NotImplementedError(f"{self.ram=}")
        return float(self.ram[:-len(" GiB")])

    @property
    def capacitystatus(self):
        return self.attributes["capacitystatus"]

    @property
    def instance_type(self):
        return self.attributes["instanceType"]

    @property
    def tenancy(self):
        return self.attributes["tenancy"]

    @property
    def sku(self):
        return self.dict_src["sku"]

    @property
    def physical_processor(self):
        return self.attributes.get("physicalProcessor")

    def print_attributes(self):
        """
        Print self attributes.

        :return:
        """

        for attr_pair in self.attributes.items():
            print(attr_pair)
