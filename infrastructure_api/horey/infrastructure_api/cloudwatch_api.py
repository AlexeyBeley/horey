"""
Standard Cloudwatch maintainer.

"""
import datetime
import time
from typing import Any

from horey.h_logger import get_logger
from horey.aws_api.base_entities.region import Region
from horey.aws_api.aws_services_entities.cloud_watch_log_group import CloudWatchLogGroup
from horey.aws_api.aws_services_entities.cloud_watch_alarm import CloudWatchAlarm
from horey.infrastructure_api.cloudwatch_api_configuration_policy import CloudwatchAPIConfigurationPolicy
logger = get_logger()


class CloudwatchAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration: CloudwatchAPIConfigurationPolicy, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api

    def provision_log_group(self, log_group_name=None):
        """
        Provision log group.

        :return:
        """

        log_group = CloudWatchLogGroup({})
        log_group.region = self.environment_api.region
        log_group.name = log_group_name or self.configuration.log_group_name
        log_group.retention_in_days = self.configuration.retention_in_days
        log_group.tags = {tag["Key"]: tag["Value"] for tag in self.environment_api.configuration.tags}
        log_group.tags["name"] = log_group.name
        self.environment_api.aws_api.cloud_watch_logs_client.provision_log_group(log_group)
        return log_group

    def get_cloudwatch_log_group(self, log_group_name=None):
        """
        Provision log group

        @return:
        """

        log_group = CloudWatchLogGroup({})
        log_group.region = self.environment_api.region
        log_group.name = log_group_name

        if self.environment_api.aws_api.cloud_watch_logs_client.update_log_group_information(log_group):
            return log_group

        self.environment_api.aws_api.cloud_watch_logs_client.clear_cache(CloudWatchLogGroup)

        if self.environment_api.aws_api.cloud_watch_logs_client.update_log_group_information(log_group):
            return log_group

        raise RuntimeError(f"Could not update log group information '{log_group_name}' in region '{self.environment_api.configuration.region}'")

    def put_cloudwatch_log_lines(self, log_group_name, lines):
        """
        Make sure the group exist and put the log lines in it.

        :param log_group_name:
        :param lines:
        :return:
        """

        log_group = self.get_cloudwatch_log_group(log_group_name)

        return self.environment_api.aws_api.cloud_watch_logs_client.put_log_lines(log_group, lines)

    # pylint: disable = unused-argument, too-many-arguments, too-many-positional-arguments, too-many-locals
    def provision_alarm(self, name=None,
                                   insufficient_data_actions=None,
                                   metric_name=None,
                                   namespace=None,
                                   statistic=None,
                                   dimensions=None,
                                   period=None,
                                   evaluation_periods=None,
                                   datapoints_to_alarm=None,
                                   threshold=None,
                                   comparison_operator=None,
                                   treat_missing_data=None,
                                   alarm_description=None,
                                   alarm_actions=None,
                                   ok_actions=None):
        """
        Provision cloudwatch metric Lambda errors.
        Lambda service metric shows the count of failed Lambda executions.

        :return:
        """

        kwargs = locals()
        del kwargs["self"]

        alarm = CloudWatchAlarm(kwargs,from_cache=True)
        base_alarm = CloudWatchAlarm({})
        for key in alarm.__dict__:
            if key not in base_alarm.__dict__:
                raise ValueError(f"Unknown key '{key}' in kwargs '{kwargs}'")
        alarm.region = self.environment_api.region
        self.environment_api.aws_api.cloud_watch_client.set_cloudwatch_alarm(alarm)

        return alarm

    def yield_logs(self, log_group_name=None, start_time=None, streams=None):
        """
        Get logs from the group.

        :param streams:
        :param log_group_name:
        :param start_time:
        :return:
        """
        log_group_name = log_group_name or self.configuration.log_group_name
        log_group = self.get_cloudwatch_log_group(log_group_name)
        # LogStreamName'|'LastEventTime
        streams = streams or self.yield_streams(log_group=log_group)

        for stream in streams:
            if start_time and stream.get_last_event_timestamp() < start_time:
                continue
            logger.info(f"Stream: {stream.name}")

            for event in self.environment_api.aws_api.cloud_watch_logs_client.yield_log_events(log_group, stream, filters_req=None):
                yield event

    def yield_streams(self, log_group=None, log_group_name=None):
        """
        Get logs from the group.

        :param log_group:
        :param log_group_name:
        :return:
        """

        log_group = log_group or self.get_cloudwatch_log_group(log_group_name)
        # LogStreamName'|'LastEventTime
        filters_req = {"orderBy": "LastEventTime", "descending": True}

        for stream in self.environment_api.aws_api.cloud_watch_logs_client.yield_log_group_streams(log_group, filters_req=filters_req):
            logger.info(f"Stream: {stream.name}")
            yield stream

    # Log queries. They call the boto3 logs client directly: the horey client retries most errors
    # (e.g. a wrong log group name) for minutes, interactive callers need to fail fast.
    # boto3 retries throttling by itself.

    FILTER_LOG_EVENTS_MAX_PAGES = 100
    INSIGHTS_FINAL_STATUSES = {"Complete", "Failed", "Cancelled", "Timeout", "Unknown"}

    def get_logs_client(self, region=None):
        """
        boto3 CloudWatch Logs client.

        :param region: region mark, e.g. "us-east-1". Default: the environment region.
        :return:
        """

        return self.environment_api.aws_api.cloud_watch_logs_client.get_session_client(
            region=Region.get_region(region) if region else self.environment_api.region)

    @staticmethod
    def to_epoch_ms(value: datetime.datetime) -> int:
        """
        Aware datetime to epoch milliseconds.

        :param value:
        :return:
        """

        return int(value.timestamp() * 1000)

    @staticmethod
    def _yield_pages(func, request: dict[str, Any], items_key: str):
        """
        Yield items of a nextToken paginated call, one page at a time: the caller stops when it has enough.

        :param func:
        :param request:
        :param items_key:
        :return:
        """

        request = dict(request)
        while True:
            response = func(**request)
            yield from response.get(items_key, [])
            if not response.get("nextToken"):
                return
            request["nextToken"] = response["nextToken"]

    def list_log_groups(self, name_prefix=None, name_contains=None, limit=50, region=None) -> list[dict[str, Any]]:
        """
        Log groups (describe_log_groups dicts).

        :param name_prefix: e.g. "/ecs/".
        :param name_contains: case-sensitive substring. Can not be combined with name_prefix.
        :param limit:
        :param region: Default: the environment region.
        :return:
        """

        if name_prefix and name_contains:
            raise ValueError("Pass name_prefix or name_contains, not both")
        request: dict[str, Any] = {"limit": min(limit, 50)}
        if name_prefix:
            request["logGroupNamePrefix"] = name_prefix
        if name_contains:
            request["logGroupNamePattern"] = name_contains

        ret = []
        for log_group in self._yield_pages(self.get_logs_client(region).describe_log_groups, request, "logGroups"):
            ret.append(log_group)
            if len(ret) >= limit:
                break
        return ret

    def list_log_streams(self, log_group_name, name_prefix=None, limit=20, region=None) -> list[dict[str, Any]]:
        """
        Log group streams (describe_log_streams dicts), the most recently written first.
        With name_prefix ordered by name: CloudWatch can not combine the two.

        :param log_group_name:
        :param name_prefix:
        :param limit:
        :param region: Default: the environment region.
        :return:
        """

        request: dict[str, Any] = {"logGroupName": log_group_name, "limit": min(limit, 50)}
        if name_prefix:
            request.update({"logStreamNamePrefix": name_prefix, "orderBy": "LogStreamName"})
        else:
            request.update({"orderBy": "LastEventTime", "descending": True})

        ret = []
        for stream in self._yield_pages(self.get_logs_client(region).describe_log_streams, request, "logStreams"):
            ret.append(stream)
            if len(ret) >= limit:
                break
        return ret

    # pylint: disable= too-many-arguments, too-many-positional-arguments
    def filter_log_events(self, log_group_name, start_time: datetime.datetime, end_time: datetime.datetime,
                          filter_pattern=None, log_stream_names=None, log_stream_name_prefix=None, limit=100,
                          region=None) -> tuple[list[dict[str, Any]], bool]:
        """
        Search the log group events in a time range, oldest first.
        At most FILTER_LOG_EVENTS_MAX_PAGES requests: pages can be empty while CloudWatch scans the range,
        the budget bounds the call duration.

        :param log_group_name:
        :param start_time: aware datetime.
        :param end_time: aware datetime.
        :param filter_pattern: CloudWatch filter syntax, e.g. "?ERROR ?Exception".
        :param log_stream_names: can not be combined with log_stream_name_prefix.
        :param log_stream_name_prefix:
        :param limit:
        :param region: Default: the environment region.
        :return: (filter_log_events event dicts, complete - the whole range was searched)
        """

        if log_stream_names and log_stream_name_prefix:
            raise ValueError("Pass log_stream_names or log_stream_name_prefix, not both")
        if start_time >= end_time:
            raise ValueError(f"start_time {start_time.isoformat()} must be before end_time {end_time.isoformat()}")

        request: dict[str, Any] = {"logGroupName": log_group_name, "startTime": self.to_epoch_ms(start_time),
                                   "endTime": self.to_epoch_ms(end_time), "limit": min(limit, 10000)}
        if filter_pattern:
            request["filterPattern"] = filter_pattern
        if log_stream_names:
            request["logStreamNames"] = log_stream_names
        if log_stream_name_prefix:
            request["logStreamNamePrefix"] = log_stream_name_prefix

        client = self.get_logs_client(region)
        events: list[dict[str, Any]] = []
        for _ in range(self.FILTER_LOG_EVENTS_MAX_PAGES):
            response = client.filter_log_events(**request)
            events += response.get("events", [])
            if not response.get("nextToken"):
                return events[:limit], len(events) <= limit
            if len(events) >= limit:
                break
            request["nextToken"] = response["nextToken"]
        return events[:limit], False

    def get_log_stream_events(self, log_group_name, log_stream_name, limit=100, start_from_head=False,
                              start_time: datetime.datetime | None = None, end_time: datetime.datetime | None = None,
                              region=None) -> list[dict[str, Any]]:
        """
        Events of a single stream in chronological order: the last limit events, or the first with start_from_head.

        :param log_group_name:
        :param log_stream_name:
        :param limit:
        :param start_from_head:
        :param start_time: aware datetime.
        :param end_time: aware datetime.
        :param region: Default: the environment region.
        :return: get_log_events event dicts.
        """

        request: dict[str, Any] = {"logGroupName": log_group_name, "logStreamName": log_stream_name,
                                   "limit": limit, "startFromHead": start_from_head}
        if start_time:
            request["startTime"] = self.to_epoch_ms(start_time)
        if end_time:
            request["endTime"] = self.to_epoch_ms(end_time)
        return self.get_logs_client(region).get_log_events(**request).get("events", [])

    def run_insights_query(self, log_group_names, query, start_time: datetime.datetime,
                           end_time: datetime.datetime, limit=100, wait_seconds=30,
                           region=None) -> tuple[str, dict[str, Any]]:
        """
        Start a Logs Insights query and wait up to wait_seconds for it to finish.

        :param log_group_names:
        :param query: e.g. "fields @timestamp, @message | filter @message like /ERROR/".
        :param start_time: aware datetime.
        :param end_time: aware datetime.
        :param limit:
        :param wait_seconds: 0 - return right after starting.
        :param region: Default: the environment region.
        :return: (query id, get_query_results response - status may still be Running)
        """

        if start_time >= end_time:
            raise ValueError(f"start_time {start_time.isoformat()} must be before end_time {end_time.isoformat()}")

        client = self.get_logs_client(region)
        query_id = client.start_query(logGroupNames=log_group_names, queryString=query,
                                      startTime=self.to_epoch_ms(start_time) // 1000,
                                      endTime=self.to_epoch_ms(end_time) // 1000, limit=limit)["queryId"]
        logger.info(f"Started Logs Insights query {query_id}")

        deadline = time.monotonic() + wait_seconds
        while True:
            response = client.get_query_results(queryId=query_id)
            if response.get("status") in self.INSIGHTS_FINAL_STATUSES or time.monotonic() >= deadline:
                return query_id, response
            time.sleep(1)

    def get_insights_query_results(self, query_id, region=None) -> dict[str, Any]:
        """
        Status and results of a Logs Insights query.

        :param query_id:
        :param region: Default: the environment region.
        :return: get_query_results response.
        """

        return self.get_logs_client(region).get_query_results(queryId=query_id)
