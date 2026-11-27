"""
MCP tools of horey.zabbix_api. Loaded by horey.mcp, see mcp/README.md.
"""

import functools
from typing import TYPE_CHECKING, Any

from horey.zabbix_api.zabbix_api import ZabbixAPI
from horey.zabbix_api.zabbix_api_configuration_policy import ZabbixAPIConfigurationPolicy

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry

SEVERITIES = ["not_classified", "information", "warning", "average", "high", "disaster"]


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    @functools.cache
    def zabbix_api() -> ZabbixAPI:
        return ZabbixAPI(registry.get_configuration(ZabbixAPIConfigurationPolicy))

    @registry.tool(read_only=True)
    def get_api_version() -> str:
        """Get the Zabbix server API version."""
        return zabbix_api().api_version()

    @registry.tool(read_only=True)
    def list_hosts(name_contains: str = "") -> list[dict[str, Any]]:
        """List the Zabbix hosts: host, name, status (0 - enabled, 1 - disabled), groups, templates, interface IPs."""
        ret = []
        for host in zabbix_api().init_hosts():
            if name_contains not in (host.host or ""):
                continue
            ret.append({"hostid": host.hostid, "host": host.host, "name": host.name, "status": host.status,
                        "groups": [group.get("name") for group in host.hostgroups or []],
                        "templates": [template.get("name") for template in host.parent_templates or []],
                        "interfaces": [interface.get("ip") or interface.get("dns") for interface in host.interfaces or []]})
        return ret

    @registry.tool(read_only=True)
    def list_templates() -> list[dict[str, Any]]:
        """List the Zabbix templates: templateid, host (technical name), name."""
        return [{"templateid": template.get("templateid"), "host": template.get("host"), "name": template.get("name")}
                for template in zabbix_api().init_templates()]

    @registry.tool(read_only=True)
    def list_problems(min_severity: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """
        List the current (unresolved) Zabbix problems, newest first: name, severity, acknowledged, start time (unix),
        hosts. min_severity: 0 - not classified, 1 - information, 2 - warning, 3 - average, 4 - high, 5 - disaster.
        """
        api = zabbix_api()
        api.login()
        problems = api.post("problem.get", params={"recent": False, "severities": list(range(min_severity, 6)),
                                                   "sortfield": ["eventid"], "sortorder": "DESC", "limit": limit})
        trigger_ids = [problem["objectid"] for problem in problems]
        hosts_by_trigger = {}
        if trigger_ids:
            for trigger in api.post("trigger.get", params={"triggerids": trigger_ids, "selectHosts": ["host"],
                                                           "output": ["triggerid"]}):
                hosts_by_trigger[trigger["triggerid"]] = [host["host"] for host in trigger.get("hosts", [])]
        return [{"eventid": problem.get("eventid"), "name": problem.get("name"),
                 "severity": SEVERITIES[int(problem.get("severity", 0))], "acknowledged": problem.get("acknowledged") == "1",
                 "clock": problem.get("clock"), "hosts": hosts_by_trigger.get(problem["objectid"], [])}
                for problem in problems]
