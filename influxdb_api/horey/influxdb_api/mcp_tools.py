"""
MCP tools of horey.influxdb_api (InfluxDB 1.x, InfluxQL). Loaded by horey.mcp, see mcp/README.md.
"""

import urllib.parse
from typing import TYPE_CHECKING, Any

from horey.influxdb_api.influxdb_api import InfluxDBAPI
from horey.influxdb_api.influxdb_api_configuration_policy import InfluxDBAPIConfigurationPolicy

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry

READ_ONLY_STATEMENT_PREFIXES = ("select", "show")


def _series_values(response: dict[str, Any]) -> list[Any]:
    """
    First column values of the first series, e.g. names in SHOW MEASUREMENTS.
    """

    series = response["results"][0].get("series") or [{}]
    return [value[0] for value in series[0].get("values", [])]


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    @registry.cached_per_configuration
    def influxdb_api(configuration_name: str | None) -> InfluxDBAPI:
        return InfluxDBAPI(registry.get_configuration(InfluxDBAPIConfigurationPolicy, configuration_name))

    def query_raw(db_name: str | None, statement: str, configuration_name: str | None = None) -> dict[str, Any]:
        database = f"db={urllib.parse.quote_plus(db_name)}&" if db_name else ""
        return influxdb_api(configuration_name).get(f"query?{database}q=" + urllib.parse.quote_plus(statement))

    @registry.tool(read_only=True)
    def list_databases(configuration_name: str | None = None) -> list[str]:
        """List the InfluxDB databases."""
        return _series_values(query_raw(None, "SHOW DATABASES", configuration_name=configuration_name))

    @registry.tool(read_only=True)
    def list_measurements(db_name: str, configuration_name: str | None = None) -> list[str]:
        """List the measurements of an InfluxDB database."""
        return _series_values(influxdb_api(configuration_name).init_measurements(db_name))

    @registry.tool(read_only=True)
    def get_measurement_schema(db_name: str, measurement: str, configuration_name: str | None = None) -> dict[str, Any]:
        """Get the tag keys and the field types of a measurement."""
        api = influxdb_api(configuration_name)
        fields_types = api.get_measurement_fields_types(db_name, measurement)
        return {"tags": api.get_measurement_tag_keys(db_name, measurement),
                "fields": {name: field_type.__name__ for name, field_type in fields_types.items()}}

    @registry.tool(read_only=True)
    def count_measurement(db_name: str, measurement: str, configuration_name: str | None = None) -> dict[str, int]:
        """Count the points of each field of a measurement."""
        return dict(influxdb_api(configuration_name).count_measurement(db_name, measurement))

    @registry.tool(read_only=True)
    def query(db_name: str, statement: str, configuration_name: str | None = None) -> dict[str, Any]:
        """
        Run a read-only InfluxQL statement (SELECT or SHOW) and return the raw result.
        Always add a LIMIT or a time range to SELECT statements.
        """
        if not statement.strip().lower().startswith(READ_ONLY_STATEMENT_PREFIXES):
            raise ValueError("Only SELECT and SHOW statements are allowed")
        return query_raw(db_name, statement, configuration_name=configuration_name)
