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
    Provision service.

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
        if self.action == "install":
            return self.install_remote()
        raise NotImplemented(self.action)

    def install_remote(self):
        """
        Isntall vrrp remotely

        :return:
        """


        self.install_keepalived_remote()
        self.configure_nftables_remote()

    def install_keepalived_remote(self):
        """
        Install keepalived

        :return:
        """

        SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir,
                                                                          self.force, self.upgrade,
                                                                          package_names=["keepalived",
                                                                                         ]).provision_remote(self.remoter)

        interfaces = self.get_interfaces_remote()
        for interface_name, interface in interfaces.items():
            network = ipaddress.IPv4Network(interface["ip"], strict=False)
            master_ip = ipaddress.IPv4Address(self.kwargs.get("master"))
            if master_ip in network:
                break
        else:
            raise ValueError(f"master ip {self.kwargs.get('master')} is not in any of the interfaces")

        host_address = interface["ip"].split("/")[0]
        if host_address == self.kwargs.get("master"):
            state = "MASTER"
        elif host_address in self.kwargs.get("backup"):
            state = "BACKUP"
        else:
            raise ValueError(f"Host address {host_address} is neither master nor backup")

        virtual_address_with_subnet = self.kwargs.get("virtual_ip_address") + "/" + interface["ip"].split("/")[1]
        config_file_path = self.generate_config_file(state, interface_name, virtual_address_with_subnet)

        return self.remoter.put_file(config_file_path, Path("/etc/keepalived") / config_file_path.name, sudo=True)

    def configure_nftables_remote(self):
        """
        Configure nftables to allow vrrp traffic

        :return:
        """

        self.remoter.execute("sudo apt install nftables -y")
        self.remoter.execute("sudo systemctl enable nftables")
        self.remoter.execute("sudo systemctl start nftables")

        # Add rules to allow VRRP traffic
        self.remoter.execute("sudo nft add table ip filter")
        self.remoter.execute("sudo nft add chain ip filter INPUT { type filter hook input priority 0 \\; }")
        self.remoter.execute("sudo nft add chain ip filter FORWARD { type filter hook forward priority 0 \\; }")
        self.remoter.execute("sudo nft add chain ip filter OUTPUT { type filter hook output priority 0 \\; }")

        # Allow VRRP multicast traffic (224.0.0.18)
        self.remoter.execute("sudo nft add rule ip filter INPUT ip daddr 224.0.0.18 udp dport 112 vrrp accept")
        self.remoter.execute("sudo nft add rule ip filter FORWARD ip daddr 224.0.0.18 udp dport 112 vrrp accept")
        self.remoter.execute("sudo nft add rule ip filter OUTPUT ip daddr 224.0.0.18 udp dport 112 vrrp accept")

        # Allow established and related connections
        self.remoter.execute("sudo nft add rule ip filter INPUT ct state established,related accept")
        self.remoter.execute("sudo nft add rule ip filter FORWARD ct state established,related accept")

        # Default drop policy
        self.remoter.execute("sudo nft add rule ip filter INPUT reject")
        self.remoter.execute("sudo nft add rule ip filter FORWARD reject")

        # Save the rules
        self.remoter.execute("sudo nft list ruleset > /etc/nftables.conf")

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
            interface_dicts[interface_name] = {"lines": lines}
            for line in lines:
                if "inet " in line:
                    interface_dicts[interface_name]["ip"] = line.strip().split()[1]
                elif "ether " in line:
                    interface_dicts[interface_name]["mac"] = line.strip().split()[1]

        return interface_dicts


    def generate_config_file(self, state, interface_name, virtual_address_with_subnet) -> Path:
        """
        Generate file

        :return:
        """

        priority = 110 if state == "MASTER" else 100

        lines = ["vrrp_instance VI_1 {",
                 f"state {state}",
                 f"interface {interface_name}",
                 "virtual_router_id 51",
                 f"priority {priority}",
                 "advert_int 1",
                 "authentication {",
                 "auth_type PASS",
                 "auth_pass somepass",
                 "}",
                 "virtual_ipaddress {",
                 virtual_address_with_subnet,
                 "}",
                 """
                 unicast_peer {
        10.0.0.2
        10.0.0.3
    }
                 """
                 
                 "}"]

        self.deployment_dir.mkdir(exist_ok=True)
        file_path = self.deployment_dir / "keepalived.conf"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))

        return file_path
