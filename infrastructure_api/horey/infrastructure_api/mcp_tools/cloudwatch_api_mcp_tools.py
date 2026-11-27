"""
MCP tools of horey.infrastructure_api CloudwatchAPI: CloudWatch Logs groups, streams, events and Insights queries.
"""

import datetime
import re
from typing import Any

from horey.infrastructure_api.cloudwatch_api import CloudwatchAPI
from horey.infrastructure_api.cloudwatch_api_configuration_policy import CloudwatchAPIConfigurationPolicy
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI
from horey.infrastructure_api.mcp_tools.base_mcp_tools import BaseMCPTools

RELATIVE_TIME_UNITS = {"s": 1, "m": 60, "h": 60 * 60, "d": 24 * 60 * 60, "w": 7 * 24 * 60 * 60}
MAX_LOG_EVENTS = 10000
MAX_INSIGHTS_WAIT_SECONDS = 60


def parse_time(value: str, now: datetime.datetime | None = None) -> datetime.datetime:
    """
    A point in time from a relative duration before now ("30s", "15m", "2h", "7d", "1w"), "now",
    or an ISO 8601 time ("2026-01-31T10:00:00Z", "2026-01-31"). Times without a time zone are UTC.

    :param value:
    :param now: Default: the current time.
    :return: aware UTC datetime.
    """

    now = now or datetime.datetime.now(datetime.timezone.utc)
    value = value.strip()
    if value.lower() in ("", "now"):
        return now

    match = re.fullmatch(r"(\d+)\s*([smhdw])", value.lower())
    if match:
        return now - datetime.timedelta(seconds=int(match.group(1)) * RELATIVE_TIME_UNITS[match.group(2)])

    try:
        ret = datetime.datetime.fromisoformat(value)
    except ValueError as error_inst:
        raise ValueError(f"Time expected as a duration (15m, 2h, 7d) or ISO 8601, received: {value!r}") from error_inst
    if ret.tzinfo is None:
        ret = ret.replace(tzinfo=datetime.timezone.utc)
    return ret.astimezone(datetime.timezone.utc)


def iso_from_ms(value: int | None) -> str | None:
    """
    Epoch milliseconds to ISO 8601 UTC.
    """

    if value is None:
        return None
    return datetime.datetime.fromtimestamp(value / 1000, datetime.timezone.utc).isoformat()


def check_limit(limit: int, maximum: int = MAX_LOG_EVENTS) -> int:
    """
    Validate a results limit.
    """

    if not 1 <= limit <= maximum:
        raise ValueError(f"limit must be between 1 and {maximum}")
    return limit


def log_event(event: dict[str, Any], max_message_chars: int) -> dict[str, Any]:
    """
    A filter_log_events / get_log_events event: time, stream and the message, truncated.
    """

    message = event.get("message", "").rstrip("\n")
    ret = {"timestamp": iso_from_ms(event.get("timestamp")), "message": message[:max_message_chars]}
    if "logStreamName" in event:
        ret["log_stream_name"] = event["logStreamName"]
    if len(message) > max_message_chars:
        ret["truncated"] = True
    return ret


class CloudwatchAPIMCPTools(BaseMCPTools):
    """
    CloudwatchAPI tools.
    """

    def cloudwatch_api(self, configuration_name: str | None) -> CloudwatchAPI:
        """
        CloudwatchAPI of the configuration environment.
        """

        return InfrastructureAPI.get_cloudwatch_api(CloudwatchAPIConfigurationPolicy(),
                                                    self.environment_api(configuration_name))

    @staticmethod
    def insights_results(response: dict[str, Any], query_id: str, limit: int) -> dict[str, Any]:
        """
        Logs Insights get_query_results response to rows of {field: value}, without @ptr.
        """

        rows = [{field["field"]: field.get("value") for field in row if field.get("field") != "@ptr"}
                for row in response.get("results", [])]
        return {"query_id": query_id, "status": response.get("status"), "results": rows[:limit],
                "statistics": response.get("statistics")}

    # pylint: disable= too-many-arguments, too-many-positional-arguments
    def register(self) -> None:
        """
        Register the tools.

        :return:
        """

        @self.registry.tool(read_only=True)
        def get_cloudwatch_log_group(log_group_name: str, configuration_name: str | None = None) -> dict[str, Any]:
            """Get a CloudWatch log group: retention, stored bytes, creation time."""
            return self.registry.to_jsonable(self.cloudwatch_api(configuration_name).get_cloudwatch_log_group(
                log_group_name))

        @self.registry.tool(read_only=True)
        def list_log_groups(name_prefix: str = "", name_contains: str = "", limit: int = 50, region: str | None = None,
                            configuration_name: str | None = None) -> list[dict[str, Any]]:
            """
            List the CloudWatch log groups of the environment region: name, stored bytes, retention days, class,
            creation time. Filter by name_prefix (e.g. "/ecs/") or name_contains (case sensitive), not both.
            """
            log_groups = self.cloudwatch_api(configuration_name).list_log_groups(
                name_prefix=name_prefix, name_contains=name_contains, limit=check_limit(limit), region=region)
            return [{"name": log_group["logGroupName"], "stored_bytes": log_group.get("storedBytes"),
                     "retention_days": log_group.get("retentionInDays"), "class": log_group.get("logGroupClass"),
                     "creation_time": iso_from_ms(log_group.get("creationTime"))} for log_group in log_groups]

        @self.registry.tool(read_only=True)
        def list_log_streams(log_group_name: str, name_prefix: str = "", limit: int = 20, region: str | None = None,
                             configuration_name: str | None = None) -> list[dict[str, Any]]:
            """
            List the streams of a log group, the most recently written first: name, first and last event times.
            With name_prefix the streams are ordered by name instead (CloudWatch can not combine the two).
            """
            streams = self.cloudwatch_api(configuration_name).list_log_streams(
                log_group_name, name_prefix=name_prefix, limit=check_limit(limit), region=region)
            return [{"name": stream["logStreamName"], "first_event_time": iso_from_ms(stream.get("firstEventTimestamp")),
                     "last_event_time": iso_from_ms(stream.get("lastEventTimestamp")),
                     "last_ingestion_time": iso_from_ms(stream.get("lastIngestionTime"))} for stream in streams]

        @self.registry.tool(read_only=True)
        def filter_log_events(log_group_name: str, filter_pattern: str = "", start_time: str = "1h", end_time: str = "",
                              log_stream_names: list[str] | None = None, log_stream_name_prefix: str = "",
                              limit: int = 100, max_message_chars: int = 2000, region: str | None = None,
                              configuration_name: str | None = None) -> dict[str, Any]:
            """
            Search the events of a log group in a time range, oldest first. Narrow the range to see the latest events.
            filter_pattern: CloudWatch filter syntax, e.g. "ERROR", "?ERROR ?Exception", '"exact phrase"',
            '{ $.level = "error" }' for JSON logs. Empty - all events.
            start_time / end_time: a duration before now ("15m", "2h", "7d") or ISO 8601 ("2026-01-31T10:00:00Z").
            Default: the last hour. Streams: log_stream_names or log_stream_name_prefix, not both.
            complete is False when the limit or the scan budget stopped the search before the end of the range:
            continue from the last event timestamp.
            """
            start, end = parse_time(start_time), parse_time(end_time)
            events, complete = self.cloudwatch_api(configuration_name).filter_log_events(
                log_group_name, start, end, filter_pattern=filter_pattern, log_stream_names=log_stream_names,
                log_stream_name_prefix=log_stream_name_prefix, limit=check_limit(limit), region=region)
            return {"events": [log_event(event, max_message_chars) for event in events], "complete": complete,
                    "start_time": start.isoformat(), "end_time": end.isoformat()}

        @self.registry.tool(read_only=True)
        def get_log_stream_events(log_group_name: str, log_stream_name: str, limit: int = 100,
                                  start_from_head: bool = False, start_time: str = "", end_time: str = "",
                                  max_message_chars: int = 2000, region: str | None = None,
                                  configuration_name: str | None = None) -> list[dict[str, Any]]:
            """
            Get the events of a single log stream in chronological order: the last limit events (tail) by default,
            the first ones with start_from_head. Find streams with list_log_streams.
            start_time / end_time (optional): a duration before now ("15m", "2h") or ISO 8601.
            """
            events = self.cloudwatch_api(configuration_name).get_log_stream_events(
                log_group_name, log_stream_name, limit=check_limit(limit), start_from_head=start_from_head,
                start_time=parse_time(start_time) if start_time else None,
                end_time=parse_time(end_time) if end_time else None, region=region)
            return [log_event(event, max_message_chars) for event in events]

        @self.registry.tool(read_only=True)
        def run_insights_query(log_group_names: list[str], query: str, start_time: str = "1h", end_time: str = "",
                               limit: int = 100, wait_seconds: int = 30, region: str | None = None,
                               configuration_name: str | None = None) -> dict[str, Any]:
            """
            Run a CloudWatch Logs Insights query over log groups (up to 50) and wait up to wait_seconds (max 60)
            for the results. If status is not Complete yet, get them later with get_insights_query_results(query_id).
            E.g. query: "fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 50",
            "stats count(*) by bin(5m)". start_time / end_time: a duration before now ("15m", "2h", "7d") or ISO 8601.
            Results are rows of {field: value}; statistics show the scanned records and bytes.
            """
            if not 0 <= wait_seconds <= MAX_INSIGHTS_WAIT_SECONDS:
                raise ValueError(f"wait_seconds must be between 0 and {MAX_INSIGHTS_WAIT_SECONDS}")
            query_id, response = self.cloudwatch_api(configuration_name).run_insights_query(
                log_group_names, query, parse_time(start_time), parse_time(end_time), limit=check_limit(limit),
                wait_seconds=wait_seconds, region=region)
            return self.insights_results(response, query_id, limit)

        @self.registry.tool(read_only=True)
        def get_insights_query_results(query_id: str, limit: int = 100, region: str | None = None,
                                       configuration_name: str | None = None) -> dict[str, Any]:
            """
            Get the status and the results of a Logs Insights query started by run_insights_query.
            Status: Scheduled, Running, Complete, Failed, Cancelled, Timeout. Results expire 7 days after the query.
            """
            response = self.cloudwatch_api(configuration_name).get_insights_query_results(query_id, region=region)
            return self.insights_results(response, query_id, check_limit(limit))
