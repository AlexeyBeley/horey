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

        """
        SystemFunctionFactory.REGISTERED_FUNCTIONS["apt_package_generic"](self.deployment_dir,
                                                                          self.force, self.upgrade,
                                                                          package_names=["keepalived",
                                                                                         ]).provision_remote(self.remoter)
        """

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

        virtual_address_with_subnet = self.kwargs.get("virtual_address") + "/" + interface["ip"].split("/")[1]
        config_file_path = self.generate_config_file(state, interface_name, virtual_address_with_subnet)

        breakpoint()
        return self.remoter.put_file(config_file_path, Path("/etc/keepalived") / config_file_path.name, sudo=True)

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
                 "}"]

        self.deployment_dir.mkdir(exist_ok=True)
        file_path = self.deployment_dir / "keepalived.conf"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))

        return file_path
