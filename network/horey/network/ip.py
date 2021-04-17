import re
import pdb

class IP:
    """
    Class for network engineers usage
    """
    ANY = None

    @staticmethod
    def any():
        if IP.ANY is None:
            IP.ANY = IP("0.0.0.0/0")
        return IP.ANY

    def __init__(self, address, **kwargs):
        self.type = None
        self.str_int_mask = None
        self.int_mask = None
        self.str_mask = None
        self.str_address = None
        self.logger = None

        # IP(value, from_dict=True)
        if "from_dict" in kwargs and kwargs["from_dict"] is True:
            if not self.init_from_dict(address):
                raise RuntimeError(f"Can not init from {address}")
            return

        if not self.init_address(address, **kwargs):
            raise RuntimeError(f"Can not init from {address}")

    def __str__(self):
        address = ""

        #  address
        if self.str_address:
            address = self.str_address

        if not address:
            raise RuntimeError("Address not set")

        #  mask
        mask = self.init_str_int_mask()

        if not mask:
            raise RuntimeError("Mask not set")

        return "{}/{}".format(address, mask)

    def __eq__(self, other):
        if not isinstance(other, IP):
            return False

        if self.str_address != other.str_address or self.int_mask != other.int_mask:
            return False

        return True

    def contains(self, ip):
        """
        Checks if self contains ip received in args as subnet

        :param ip: IP
        :return: bool
        """
        raise NotImplementedError("contains")

    def intersect(self, ip):
        """
        Returns the intersection between two networks

        :param ip:
        :return: IP
        """

        if not isinstance(ip, IP):
            raise ValueError("{} is not an IP".format(ip))

        if self == self.any():
            return ip.copy()

        if ip == self.any():
            return self

        int_min_mask = min(self.init_int_mask(), ip.init_int_mask())
        str_bit_common = self.init_str_bit_address()[:int_min_mask]

        if str_bit_common != ip.init_str_bit_address()[:int_min_mask]:
            return

        if int_min_mask == self.init_int_mask():
            ret_ip = self
        else:
            ret_ip = ip

        return ret_ip.first_in_net()

    def first_in_net(self):
        if self.type == IP.Types.IPV4:
            type_mask_len = 32
        else:
            type_mask_len = 128

        mask_len = self.init_int_mask()
        str_address = "{}{}".format(self.init_str_bit_address()[:mask_len], "0"*(type_mask_len-mask_len))
        str_address = self.address_from_str_binary(str_address)
        ip_ret = IP("{}/{}".format(str_address, str(mask_len)))
        return ip_ret

    def address_from_str_binary(self, str_address):
        return ".".join([str(int(str_address[i*8: i*8 + 8], 2)) for i in range(0, 4)])

    def init_from_dict(self, dict_src):
        if self.str_address or self.str_int_mask:
            raise ValueError(dict_src)
        else:
            self.type = dict_src["type"]
            self.str_address = dict_src["str_address"]
            self.str_int_mask = dict_src["str_int_mask"]
            return True

    def init_address(self, str_src, **kwargs):
        if "logger" in kwargs:
            self.logger = kwargs["logger"]

        if "." in str_src:
            self.type = IP.Types.IPV4

        if ":" in str_src:
            self.type = IP.Types.IPV6

        self.str_mask = None
        self.str_int_mask = None
        self.int_mask = None

        if "str_mask" in kwargs:
            raise NotImplementedError()

        if "int_mask" in kwargs:
            if "/" in str_src:
                raise NotImplementedError()
            self.int_mask = kwargs["int_mask"]

        if "/" in str_src:
            if (self.str_mask is not None) or \
                    (self.int_mask is not None) or \
                    (self.str_int_mask is not None):
                raise NotImplementedError()

            self.str_address, str_mask = str_src.split("/")

            if str_mask.isdigit():
                self.str_int_mask = str_mask
            else:
                self.str_mask = str_mask
        else:
            self.str_address = str_src
        return True

    def init_int_mask(self):
        if self.int_mask is None:
            if not self.str_int_mask:
                raise NotImplementedError()
            self.int_mask = int(self.str_int_mask)

        return self.int_mask

    def init_str_address(self):
        if self.str_address:
            return self.str_address
        else:
            raise NotImplementedError()

    def init_str_bit_address(self):
        return "".join([format(int(octet), '08b') for octet in self.str_address.split(".")])

    def init_str_int_mask(self):
        if self.str_int_mask:
            return self.str_int_mask
        elif self.int_mask is not None:
            self.str_int_mask = str(self.int_mask)
        else:
            raise NotImplementedError()

        return self.str_int_mask

    @property
    def str_int_mask(self):
        return self._str_int_mask

    @str_int_mask.setter
    def str_int_mask(self, value):
        if value is None:
            self._str_int_mask = None
            return

        if self.type == IP.Types.IPV4:
            if not IP.check_str_int_mask_v4_validity(value):
                raise NotImplementedError()
        elif self.type == IP.Types.IPV6:
            if not IP.check_str_int_mask_v6_validity(value):
                raise NotImplementedError()
        else:
            raise NotImplementedError()

        self._str_int_mask = value

    @property
    def int_mask(self):
        return self._int_mask

    @int_mask.setter
    def int_mask(self, value):
        if value is None:
            self._int_mask = None
            return

        if self.type == IP.Types.IPV4:
            if not IP.check_int_mask_v4_validity(value):
                raise NotImplementedError()
        elif self.type == IP.Types.IPV6:
            if not IP.check_int_mask_v6_validity(value):
                raise NotImplementedError()
        else:
            raise NotImplementedError()

        self._int_mask = value

    @property
    def str_mask(self):
        return self._str_mask

    @str_mask.setter
    def str_mask(self, value):
        if value is None:
            self._str_mask = None
            return

        raise NotImplementedError()
        self._str_mask = value

    @property
    def str_address(self):
        return self._str_address

    @str_address.setter
    def str_address(self, value):
        if value is None:
            self._str_address = None
            return

        if self.type == IP.Types.IPV4:
            if not IP.check_ipv4_validity(value):
                raise Exception
        elif self.type == IP.Types.IPV6:
            if not IP.check_ipv6_validity(value):
                raise ValueError(value)
        else:
            raise Exception

        self._str_address = value

    def _log(self, str_src):
        if self.logger:
            self.logger.error(str_src)

    def init_host(self, str_address, **kwargs):
        return self.init_address(str_address, int_mask=32)

    @staticmethod
    def check_ipv4_validity(str_src):
        lst_src = str_src.split(".")
        if len(lst_src) != 4:
            return False

        try:
            for str_oct in lst_src:
                int_oct = int(str_oct)
                if int_oct < 0 or int_oct > 255:
                    return False
        except Exception:
            return False

        return True

    @staticmethod
    def convert_short_to_long_lst_ipv6(str_src):
        lst_ret = []
        if "::" in str_src:
            pre, post = str_src.split("::")
            count = 0
            if pre:
                count += len(pre.split(":"))
            if post:
                count += len(post.split(":"))
            str_src = str_src.replace("::", ":"+":".join(["0000" for x in range(8-count)])+":")
            str_src = str_src.strip(":")

        lst_src = str_src.split(":")

        for str_group in lst_src:
            if str_group:
                if len(str_group) < 4:
                    str_group = "0" * (4 - len(str_group)) + str_group
                lst_ret.append(str_group)
            else:
                lst_ret.append("0000")

        return lst_ret

    @staticmethod
    def check_ipv6_validity(str_src):
        lst_long_address = IP.convert_short_to_long_lst_ipv6(str_src)
        if len(lst_long_address) != 8:
            return False

        try:
            for str_part in lst_long_address:
                pattern = re.compile("^[a-f0-9]{4}$")
                match_part = re.match(pattern, str_part)
                if not match_part:
                    return False
        except Exception:
            return False

        return True

    @staticmethod
    def check_ip_validity(str_src):
        if "." in str_src:
            return IP.check_ipv4_validity(str_src)

        if ":" in str_src:
            return IP.check_ipv6_validity(str_src)

        raise Exception

    @staticmethod
    def check_str_int_mask_v4_validity(str_src):
        if type(str_src) is not str:
            return False

        if not str_src.isdigit():
            return False

        return IP.check_int_mask_v4_validity(int(str_src))

    @staticmethod
    def check_str_int_mask_v6_validity(str_src):
        if type(str_src) is not str:
            return False

        if not str_src.isdigit():
            return False

        return IP.check_int_mask_v6_validity(int(str_src))

    @staticmethod
    def check_int_mask_v4_validity(int_src):
        if type(int_src) is not int:
            return False

        if int_src < 0 or int_src > 32:
            return False

        return True

    @staticmethod
    def check_int_mask_v6_validity(int_src):
        if type(int_src) is not int:
            return False

        if int_src < 0 or int_src > 128:
            return False

        return True

    class Types:
        """Enum simulation"""

        IPV4 = "IPv4"
        IPV6 = "IPv6"

    def convert_to_dict(self):
        return {
                "str_address": self.init_str_address(),
                "str_int_mask": self.init_str_int_mask(),
                "type": self.type
               }

    def copy(self):
        ip = IP(self.init_str_address(), int_mask=self.init_int_mask())
        return ip
