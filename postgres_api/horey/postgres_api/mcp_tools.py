"""
MCP tools of horey.postgres_api. Loaded by horey.mcp, see mcp/README.md.
"""

import functools
from typing import TYPE_CHECKING, Any

from sqlalchemy import text

from horey.postgres_api.postgres_api import PostgresAPI
from horey.postgres_api.postgres_api_configuration_policy import PostgresAPIConfigurationPolicy

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    @functools.cache
    def postgres_api() -> PostgresAPI:
        return PostgresAPI(registry.get_configuration(PostgresAPIConfigurationPolicy))

    def query_read_only(statement: str, parameters: dict[str, Any] | None = None, limit: int = 200) -> list[dict[str, Any]]:
        """
        Run in a READ ONLY transaction: the database rejects any change.
        """

        with postgres_api().engine.connect() as connection:
            with connection.begin():
                connection.execute(text("SET TRANSACTION READ ONLY"))
                result = connection.execute(text(statement), parameters or {})
                if not result.returns_rows:
                    return []
                return registry.to_jsonable([dict(row) for row in result.mappings().fetchmany(limit)])

    @registry.tool(read_only=True)
    def check_connection() -> bool:
        """Check the configured PostgreSQL database is reachable."""
        return postgres_api().check_connection()

    @registry.tool(read_only=True)
    def list_tables(schema: str = "public") -> list[dict[str, Any]]:
        """List the tables and views of a schema with their estimated rows count."""
        return query_read_only(
            "SELECT t.table_name, t.table_type, c.reltuples::bigint AS estimated_rows "
            "FROM information_schema.tables t "
            "LEFT JOIN pg_class c ON c.relname = t.table_name "
            "LEFT JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = t.table_schema "
            "WHERE t.table_schema = :schema ORDER BY t.table_name",
            {"schema": schema}, limit=10000)

    @registry.tool(read_only=True)
    def describe_table(table_name: str, schema: str = "public") -> list[dict[str, Any]]:
        """Get the columns of a table: name, type, nullable, default."""
        return query_read_only(
            "SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns "
            "WHERE table_schema = :schema AND table_name = :table_name ORDER BY ordinal_position",
            {"schema": schema, "table_name": table_name}, limit=10000)

    @registry.tool(read_only=True)
    def query(statement: str, parameters: dict[str, Any] | None = None, limit: int = 200) -> list[dict[str, Any]]:
        """
        Run a SQL query in a read-only transaction and return up to limit rows.
        Use :name placeholders with parameters, e.g. "SELECT * FROM items WHERE id = :id", {"id": 1}.
        """
        return query_read_only(statement, parameters, limit=limit)

    @registry.tool(destructive=True)
    def execute(statement: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """
        Execute a SQL statement which changes data or schema (INSERT, UPDATE, DELETE, DDL) in its own transaction.
        Use query for reads. Use :name placeholders with parameters.
        """
        return registry.to_jsonable(postgres_api().execute(statement, parameters or {}))
