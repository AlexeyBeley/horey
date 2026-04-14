"""
Provision ntp service.

"""
import ipaddress
import threading
from pathlib import Path

from horey.provision_constructor.system_function_factory import SystemFunctionFactory

from horey.provision_constructor.system_functions.system_function_common import (
    SystemFunctionCommon,
)
from horey.common_utils.bash_executor import BashExecutor
from horey.common_utils.remoter import Remoter
from horey.h_logger import get_logger

logger = get_logger()
BashExecutor.set_logger(logger, override=False)


@SystemFunctionFactory.register
class Provisioner(SystemFunctionCommon):
    """
    Provision NAT.

    """
    LOCK = threading.Lock()

    def __init__(self, deployment_dir, force, upgrade, **kwargs):
        """

        :param deployment_dir:
        :param force:
        :param upgrade:
        :param kwargs:
        """
        super().__init__(deployment_dir, force, upgrade, **kwargs)

    def provision_remote(self, remoter: Remoter):
        """
        Provision remotely

        :param remoter:
        :return:
        """

        self.remoter = remoter
        if self.action == "get_interfaces":
            return self.get_interfaces_remote()
        if self.action == "find_interface_by_net":
            return self.find_interface_by_net(self.kwargs.get("network"), interfaces=self.kwargs.get("interfaces"))
        raise NotImplemented(self.action)

    def find_interface_by_net(self, desired_network:str, ignore_addresses=None, interfaces=None):
        """
        Go over interfaces and find the one in the network

        :param interfaces:
        :param ignore_addresses:
        :param desired_network:
        :return:
        """

        network = ipaddress.IPv4Network(desired_network, strict=False)
        ignore_addresses = ignore_addresses or []
        interfaces = interfaces or self.get_interfaces_remote()
        for interface_name, interface in interfaces.items():
            if len(interface["ip"]) == 0:
                continue
            for str_ip_address in interface["ip"]:
                str_ip_address_raw = str_ip_address.split("/")[0]
                if str_ip_address_raw not in ignore_addresses:
                    break
            else:
                raise RuntimeError(f"Was not able to find IP address: {interface_name=}")


            ip_address = ipaddress.IPv4Address(str_ip_address_raw)
            if ip_address in network:
                return interface

        raise ValueError(f"Was not able to find interface in network {self.kwargs.get('network')}")


    def get_interfaces_remote(self) -> dict:
        """
        Init interfaces data

        :return:
        """

        interface_lines = {}

        aggregator = []
        interface_name = None

        ret = self.remoter.execute("ip addr show")
        for line in ret[0]:
            line_parts = line.split(":")
            if line_parts and line_parts[0].isdigit():
                if interface_name:
                    interface_lines[interface_name] = aggregator
                aggregator = []
                interface_name = line_parts[1].strip()
            aggregator.append(line)

        interface_lines[interface_name] = aggregator

        interface_dicts = {}

        for interface_name, lines in interface_lines.items():
            interface_dicts[interface_name] = {"lines": lines, "ip": []}
            for line in lines:
                if "inet " in line:
                    interface_dicts[interface_name]["ip"].append(line.strip().split()[1])
                elif "ether " in line:
                    interface_dicts[interface_name]["mac"] = line.strip().split()[1]

        return interface_dicts

