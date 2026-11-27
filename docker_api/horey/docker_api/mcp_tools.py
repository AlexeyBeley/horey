"""
MCP tools of horey.docker_api. Loaded by horey.mcp, see mcp/README.md.
No configuration file: the local Docker daemon is used. In the horey MCP container mount the socket:
-v /var/run/docker.sock:/var/run/docker.sock
"""

import functools
from typing import TYPE_CHECKING, Any

from horey.docker_api.docker_api import DockerAPI

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools. Containers are read with the docker SDK client: DockerAPI.get_containers_bash needs the docker CLI.

    :param registry: passed in by horey.mcp
    """

    @functools.cache
    def docker_api() -> DockerAPI:
        return DockerAPI()

    @registry.tool(read_only=True)
    def list_images(repo_name: str | None = None) -> list[dict[str, Any]]:
        """List the local Docker images: short id, tags, created, size in bytes. Optional repository filter."""
        return [{"id": image.short_id, "tags": image.tags, "created": image.attrs.get("Created"),
                 "size": image.attrs.get("Size")} for image in docker_api().get_all_images(repo_name=repo_name)]

    @registry.tool(read_only=True)
    def list_containers(all_containers: bool = False) -> list[dict[str, Any]]:
        """List the Docker containers (running only, unless all_containers): short id, name, image, status."""
        return [{"id": container.short_id, "name": container.name,
                 "image": container.image.tags[0] if container.image.tags else container.image.short_id,
                 "status": container.status}
                for container in docker_api().client.containers.list(all=all_containers)]

    @registry.tool(read_only=True)
    def get_container_logs(container_name: str, tail_lines: int = 200) -> str:
        """Get the last tail_lines lines of a Docker container's logs (stdout and stderr)."""
        container = docker_api().client.containers.get(container_name)
        return container.logs(tail=tail_lines).decode("utf-8", errors="replace")

    @registry.tool()
    def pull_image(repo: str, tag: str | None = None) -> list[str]:
        """Pull a Docker image, e.g. repo "python", tag "3.14-slim". Returns the pulled image tags."""
        return [tag_name for image in docker_api().pull_images(repo, tag=tag) for tag_name in image.tags]
