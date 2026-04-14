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
        if self.action == "install":
            return self.install_remote()
        raise NotImplemented(self.action)

    def install_remote(self):
        """
        Isntall vrrp remotely

        :return:
        """

        self.configure_nftables_remote()

    def configure_nftables_remote(self):
        """
        Configure nftables to allow NAT traffic

        :return:
        """

        interfaces = SystemFunctionFactory.REGISTERED_FUNCTIONS["net"](self.deployment_dir,
                                                                       self.force,
                                                                       self.upgrade,
                                                                       action="get_interfaces"
                                                                       ).provision_remote(self.remoter)

        interface = SystemFunctionFactory.REGISTERED_FUNCTIONS["net"](self.deployment_dir,
                                                                      self.force,
                                                                      self.upgrade,
                                                                      action="find_interface_by_net",
                                                                      interfaces=interfaces,
                                                                      network=self.kwargs.get(
                                                                          "src_network")).provision_remote(self.remoter)
        breakpoint()

        self.remoter.execute("sudo apt install nftables -y")
        self.remoter.execute("sudo systemctl enable nftables")
        self.remoter.execute("sudo systemctl start nftables")

        # Create NAT table and chains
        self.remoter.execute("sudo nft add table ip nat")
        self.remoter.execute("sudo nft add chain ip nat PREROUTING { type nat hook prerouting priority -100 \\; }")
        self.remoter.execute("sudo nft add chain ip nat POSTROUTING { type nat hook postrouting priority 100 \\; }")

        # Create filter table and chains
        self.remoter.execute("sudo nft add table ip filter")
        self.remoter.execute("sudo nft add chain ip filter INPUT { type filter hook input priority 0 \\; }")
        self.remoter.execute("sudo nft add chain ip filter FORWARD { type filter hook forward priority 0 \\; }")
        self.remoter.execute("sudo nft add chain ip filter OUTPUT { type filter hook output priority 0 \\; }")

        # Enable NAT masquerading for traffic from ens5 subnet going out ens6
        self.remoter.execute("sudo nft add rule ip nat POSTROUTING oifname ens6 ip saddr 10.10.49.0/24 masquerade")

        # Allow forwarding from ens5 to ens6
        self.remoter.execute(
            "sudo nft add rule ip filter FORWARD iifname ens5 oifname ens6 ip saddr 10.10.49.0/24 accept")
        self.remoter.execute(
            "sudo nft add rule ip filter FORWARD iifname ens6 oifname ens5 ip daddr 10.10.49.0/24 ct state related,established accept")

        # Enable IP forwarding
        self.remoter.execute("sudo sysctl -w net.ipv4.ip_forward=1")

        # route traffic
        # Allow input traffic on both interfaces
        self.remoter.execute("sudo nft add rule ip filter INPUT iifname ens5 accept")
        self.remoter.execute("sudo nft add rule ip filter INPUT iifname ens6 ct state related,established accept")

        # Allow loopback traffic
        self.remoter.execute("sudo nft add rule ip filter INPUT iifname lo accept")

        # Set default policies (optional but recommended)
        self.remoter.execute("sudo nft add rule ip filter INPUT drop")
        self.remoter.execute("sudo nft add rule ip filter FORWARD drop")

        # Make IP forwarding persistent
        self.remoter.execute("echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf")

        # Save the rules
        breakpoint()
        self.remoter.execute("sudo sh -c 'nft list ruleset > /etc/nftables.conf'")

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

    def generate_config_file(self, state, interface_name, virtual_address_with_subnet, unicast_peers) -> Path:
        """
        Generate file
        Protocol 112

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
                 "unicast_peer {",
                 *unicast_peers,
                 "}",
                 "}"]

        self.deployment_dir.mkdir(exist_ok=True)
        file_path = self.deployment_dir / "keepalived.conf"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))

        return file_path
