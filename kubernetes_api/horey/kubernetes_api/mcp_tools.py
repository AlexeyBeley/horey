"""
MCP tools of horey.kubernetes_api. Loaded by horey.mcp, see mcp/README.md.
The configuration file (kubernetes_api_configuration.py|json) sets endpoint, token and cadata.
"""

import functools
from typing import TYPE_CHECKING, Any

from horey.kubernetes_api.kubernetes_api import KubernetesAPI
from horey.kubernetes_api.kubernetes_api_configuration_policy import KubernetesAPIConfigurationPolicy

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def _metadata(dict_src: dict[str, Any]) -> dict[str, Any]:
    metadata = dict_src.get("metadata") or {}
    return {"name": metadata.get("name"), "namespace": metadata.get("namespace")}


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools. The client is used directly: KubernetesAPI.init_* also write cache files.

    :param registry: passed in by horey.mcp
    """

    @functools.cache
    def kubernetes_api() -> KubernetesAPI:
        return KubernetesAPI(registry.get_configuration(KubernetesAPIConfigurationPolicy))

    @registry.tool(read_only=True)
    def list_namespaces() -> list[str]:
        """List the Kubernetes namespaces."""
        return [_metadata(namespace.dict_src)["name"] for namespace in kubernetes_api().client.get_namespaces()]

    @registry.tool(read_only=True)
    def list_pods(namespace: str = "") -> list[dict[str, Any]]:
        """List the pods (all namespaces or one): name, namespace, phase, node, ready containers, restarts."""
        ret = []
        for pod in kubernetes_api().client.get_pods():
            pod_dict = _metadata(pod.dict_src)
            if namespace and pod_dict["namespace"] != namespace:
                continue
            status = pod.dict_src.get("status") or {}
            container_statuses = status.get("container_statuses") or []
            pod_dict.update({
                "phase": status.get("phase"),
                "node": (pod.dict_src.get("spec") or {}).get("node_name"),
                "ready": f"{sum(1 for container in container_statuses if container.get('ready'))}/{len(container_statuses)}",
                "restarts": sum(container.get("restart_count") or 0 for container in container_statuses),
            })
            ret.append(pod_dict)
        return ret

    @registry.tool(read_only=True)
    def list_deployments(namespace: str | None = None) -> list[dict[str, Any]]:
        """List the deployments: name, namespace, desired/ready/available replicas, images."""
        ret = []
        for deployment in kubernetes_api().client.get_deployments(namespace=namespace):
            spec = deployment.dict_src.get("spec") or {}
            status = deployment.dict_src.get("status") or {}
            containers = ((spec.get("template") or {}).get("spec") or {}).get("containers") or []
            deployment_dict = _metadata(deployment.dict_src)
            deployment_dict.update({"replicas": spec.get("replicas"), "ready_replicas": status.get("ready_replicas"),
                                    "available_replicas": status.get("available_replicas"),
                                    "images": [container.get("image") for container in containers]})
            ret.append(deployment_dict)
        return ret

    @registry.tool(read_only=True)
    def list_services(namespace: str | None = None) -> list[dict[str, Any]]:
        """List the services: name, namespace, type, cluster IP, ports."""
        ret = []
        for service in kubernetes_api().client.get_services(namespace=namespace):
            spec = service.dict_src.get("spec") or {}
            service_dict = _metadata(service.dict_src)
            service_dict.update({"type": spec.get("type"), "cluster_ip": spec.get("cluster_ip"),
                                 "ports": [{"port": port.get("port"), "target_port": port.get("target_port"),
                                            "protocol": port.get("protocol")} for port in spec.get("ports") or []]})
            ret.append(service_dict)
        return ret

    @registry.tool(read_only=True)
    def list_ingresses(namespace: str | None = None) -> list[dict[str, Any]]:
        """List the ingresses: name, namespace, hosts."""
        ret = []
        for ingress in kubernetes_api().client.get_ingresses(namespace=namespace):
            spec = ingress.dict_src.get("spec") or {}
            ingress_dict = _metadata(ingress.dict_src)
            ingress_dict["hosts"] = [rule.get("host") for rule in spec.get("rules") or []]
            ret.append(ingress_dict)
        return ret
