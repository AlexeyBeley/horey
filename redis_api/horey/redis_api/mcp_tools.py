"""
MCP tools of horey.redis_api. Loaded by horey.mcp, see mcp/README.md.
"""

import functools
from typing import TYPE_CHECKING, Any

from horey.redis_api.redis_api import RedisAPI
from horey.redis_api.redis_api_configuration_policy import RedisAPIConfigurationPolicy

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    @functools.cache
    def redis_api() -> RedisAPI:
        return RedisAPI(registry.get_configuration(RedisAPIConfigurationPolicy))

    @registry.tool(read_only=True)
    def get_stream_length(stream_name: str) -> int:
        """Get the number of messages in a Redis stream."""
        return redis_api().client.xlen(stream_name)

    @registry.tool(read_only=True)
    def peek_stream(stream_name: str, count: int = 20) -> list[dict[str, Any]]:
        """Read the oldest messages of a Redis stream without removing them: id and fields."""
        return [{"id": registry.to_jsonable(message_id), "fields": registry.to_jsonable(fields)}
                for message_id, fields in redis_api().client.xrange(stream_name, count=count)]

    @registry.tool()
    def write_stream(stream_name: str, fields: dict[str, str]) -> str:
        """Add a message to a Redis stream. Returns the message id."""
        return str(registry.to_jsonable(redis_api().write_stream(stream_name, fields)))

    @registry.tool(destructive=True)
    def consume_stream(stream_name: str, count: int | None = None) -> list[dict[str, Any]]:
        """Read messages from a Redis stream and DELETE them from it (the consumers will not get them)."""
        return [{"id": registry.to_jsonable(message_id), "fields": registry.to_jsonable(fields)}
                for message_id, fields in redis_api().read_stream(stream_name, count=count)]
