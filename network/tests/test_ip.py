import os
import pdb
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from horey.network.ip import IP


def test_ip_init(self):
    ip = IP("10.0.0.1/24")
    self.assertTrue(isinstance(ip, IP))

    # @unittest.skip("todo:")
def test_convert_short_to_long_ipv6(self):
    assert IP.convert_short_to_long_lst_ipv6("::") == ["0000", "0000", "0000", "0000", "0000", "0000", "0000", "0000"]
    assert IP.convert_short_to_long_lst_ipv6("::1100") == ["0000", "0000", "0000", "0000", "0000", "0000", "0000", "1100"]
    assert IP.convert_short_to_long_lst_ipv6("0::1") == ["0000", "0000", "0000", "0000", "0000", "0000", "0000", "0001"]
    assert IP.convert_short_to_long_lst_ipv6("1:10::1") == ["0001", "0010", "0000", "0000", "0000", "0000", "0000", "0001"]
    assert IP.convert_short_to_long_lst_ipv6("1:10::10:1") == ["0001", "0010", "0000", "0000", "0000", "0000", "0010", "0001"]
    assert IP.convert_short_to_long_lst_ipv6("1::10:1") == ["0001", "0000", "0000", "0000", "0000", "0000", "0010", "0001"]
    assert IP.convert_short_to_long_lst_ipv6("1:1:1:1:1:1:1:1") == ["0001", "0001", "0001", "0001", "0001", "0001", "0001", "0001"]

    # @unittest.skip("todo:")
def test_compare(self):
    self.assertEqual(IP("10.0.0.1/24"), IP("10.0.0.1/24"))

    # @unittest.skip("todo:")
def test_init_str_bit_address(self):
    ip = IP("10.0.0.1/24")
    self.assertEqual(ip.init_str_bit_address(), "00001010000000000000000000000001")

    # @unittest.skip("todo:")
def test_address_from_str_binary(self):
    ip = IP("10.0.0.1/24")
    self.assertEqual(ip.address_from_str_binary("00001010000000000000000000000001"), "10.0.0.1")

    # @unittest.skip("todo:")
def test_first_in_net(self):
    ip = IP("10.0.0.1/24")
    self.assertEqual(ip.first_in_net(), IP("10.0.0.0/24"))

def test_split():
    ip = IP("10.0.0.0/22")
    lst_ret = ip.split(24)
    assert lst_ret == 0


if __name__ == "__main__":
    test_split()