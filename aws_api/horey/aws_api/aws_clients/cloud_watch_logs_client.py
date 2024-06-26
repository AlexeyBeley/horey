"""
AWS client to handle cloud watch logs.
"""
import datetime
import time
import uuid

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.cloud_watch_log_group import CloudWatchLogGroup
from horey.aws_api.aws_services_entities.cloud_watch_log_group_metric_filter import (
    CloudWatchLogGroupMetricFilter,
)
from horey.aws_api.aws_services_entities.cloud_watch_log_stream import (
    CloudWatchLogStream,
)
from horey.h_logger import get_logger

logger = get_logger()


class CloudWatchLogsClient(Boto3Client):
    """
    Client to work with cloud watch logs API.
    """

    NEXT_PAGE_REQUEST_KEY = "nextToken"
    NEXT_PAGE_RESPONSE_KEY = "nextToken"
    NEXT_PAGE_INITIAL_KEY = ""

    def __init__(self):
        client_name = "logs"
        super().__init__(client_name)

    # pylint: disable= too-many-arguments
    def yield_log_groups(self, region=None, update_info=False, filters_req=None, get_tags=True):
        """
        Yield log_groups

        :return:
        """

        get_tags_callback = self.get_tags if get_tags else None
        regional_fetcher_generator = self.yield_log_groups_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            CloudWatchLogGroup,
                                                            update_info=update_info,
                                                            full_information_callback=None,
                                                            get_tags_callback=get_tags_callback,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_log_groups_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """
        yield from self.execute(
                self.get_session_client(region=region).describe_log_groups, "logGroups", filters_req=filters_req
        )

    def get_cloud_watch_log_groups(self):
        """
        Be sure you know what you do, when you set full_information=True.
        This can kill your memory, if you have a lot of data in cloudwatch.
        Better using yield_log_group_streams_raw if you need.

        :return:
        """

        return list(self.yield_log_groups())

    def get_region_cloud_watch_log_groups(self, region, get_tags=True, update_info=False):
        """
        Get region log groups.

        :param update_info:
        :param region:
        :param get_tags:
        :return:
        """

        return list(self.yield_log_groups(region=region, get_tags=get_tags, update_info=update_info))

    def yield_log_group_metric_filters(self, region=None, update_info=False, filters_req=None):
        """
        Yield log_group_metric_filters

        :return:
        """

        regional_fetcher_generator = self.yield_log_group_metric_filters_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                                 CloudWatchLogGroupMetricFilter,
                                                                 update_info=update_info,
                                                                 regions=[region] if region else None,
                                                                 filters_req=filters_req)

    def yield_log_group_metric_filters_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
                self.get_session_client(region=region).describe_metric_filters, "metricFilters", filters_req=filters_req
        )

    def get_log_group_metric_filters(self):
        """
        Get all metric filters in all regions

        :return:
        """

        return list(self.yield_log_group_metric_filters())

    def get_region_log_group_metric_filters(self, region):
        """
        Get all metric filters in a region

        :return:
        @param region:
        """

        return list(self.yield_log_group_metric_filters(region=region))

    def yield_log_group_streams_raw(self, log_group):
        """
        Yields streams - made to handle large log groups, in order to prevent the OOM collapse.
        :param log_group:
        :return:
        """

        yield from self.execute(
                self.get_session_client(region=log_group.region).describe_log_streams,
                "logStreams",
                filters_req={"logGroupName": log_group.name},
        )

    def yield_log_group_streams(self, log_group):
        """
        Yields streams - made to handle large log groups, in order to prevent the OOM collapse.
        :param log_group:
        :return:
        """

        for response in self.execute(
                self.get_session_client(region=log_group.region).describe_log_streams,
                "logStreams",
                filters_req={"logGroupName": log_group.name},
        ):
            yield CloudWatchLogStream(response)

    def provision_metric_filter(self, metric_filter: CloudWatchLogGroupMetricFilter):
        """
        Standard.

        :param metric_filter:
        :return:
        """

        request_dict = metric_filter.generate_create_request()
        logger.info(
            f"Creating cloudwatch log group metric filter in region '{metric_filter.region}': {request_dict}"
        )
        for response in self.execute(
                self.get_session_client(region=metric_filter.region).put_metric_filter, "ResponseMetadata",
                filters_req=request_dict
        ):
            if response["HTTPStatusCode"] != 200:
                raise RuntimeError(f"{response}")

    def yield_log_events(self, log_group: CloudWatchLogGroup, stream):
        """

        # todo: refactor
        for response in self.execute(
                self.get_session_client(region=region).get_log_events,
                "events",
                raw_data=True,
                filters_req={
                    "logGroupName": log_group.name,
                    "logStreamName": stream.name,
                    "nextToken": token,
                },
        ):
            if token != response["nextForwardToken"]:
                raise ValueError()

        :param log_group:
        :return:
        """

        self.NEXT_PAGE_RESPONSE_KEY = "nextForwardToken"
        token = None
        new_token = None
        stop = False
        while not stop:
            filters_req = {
                "logGroupName": log_group.name,
                "logStreamName": stream.name,
                "startFromHead": True,
            }
            if token is not None:
                filters_req["nextToken"] = token

            for response in self.execute(
                    self.get_session_client(region=log_group.region).get_log_events,
                    "events",
                    raw_data=True,
                    filters_req=filters_req,
            ):
                new_token = response["nextForwardToken"]
                logger.info(f"old token: {token} new token: {new_token}")
                if new_token == token:
                    return
                logger.info(f"Extracted {len(response['events'])} events")
                yield from response["events"]
                time.sleep(10)

            token = new_token
        return

    def update_log_group_information(self, log_group, update_info=False):
        """
        Standard.

        :param log_group:
        :return:
        """

        region_log_groups = self.get_region_cloud_watch_log_groups(log_group.region, get_tags=False, update_info=update_info)
        for region_log_group in region_log_groups:
            if region_log_group.name == log_group.name:
                filters_req = {"logGroupNamePattern": log_group.name}
                full_info_log_groups = list(
                    self.yield_log_groups(region=log_group.region, update_info=True, filters_req=filters_req,
                                          get_tags=True))
                if len(full_info_log_groups) == 0:
                    return False
                if len(full_info_log_groups) > 1:
                    raise RuntimeError(f"Found {[x.name for x in full_info_log_groups]} log groups with params: {filters_req}")
                log_group.update_from_raw_response(full_info_log_groups[0].dict_src)
                return True
        return False

    def provision_log_group(self, log_group: CloudWatchLogGroup):
        """
        Standard.

        :param log_group:
        :return:
        """
        log_group_current = CloudWatchLogGroup({"name": log_group.name})
        log_group_current.region = log_group.region
        if self.update_log_group_information(log_group_current):
            delete_request, put_request = log_group_current.generate_retention_policy_requests(log_group)
            if delete_request and put_request:
                raise RuntimeError(f"Can not be both: {delete_request=}, {put_request=}")

            if delete_request:
                for _ in self.execute(self.get_session_client(region=log_group.region).delete_retention_policy, None,
                                      raw_data=True, filters_req=delete_request):
                    self.clear_cache(CloudWatchLogGroup)

            if put_request:
                for _ in self.execute(self.get_session_client(region=log_group.region).put_retention_policy, None,
                                      raw_data=True, filters_req=put_request):
                    self.clear_cache(CloudWatchLogGroup)
        else:
            self.provision_log_group_raw(log_group.region, log_group.generate_create_request())

        for i in range(60):
            if self.update_log_group_information(log_group, update_info=True):
                break
            logger.info(f"Going to sleep after {i} retries")
            time.sleep(1)
        else:
            raise RuntimeError(f"Was not able to find log_group {log_group.name}")

    def provision_log_group_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Creating log group '{request_dict}'")
        for response in self.execute(
                self.get_session_client(region=region).create_log_group, None, raw_data=True, filters_req=request_dict
        ):
            self.clear_cache(CloudWatchLogGroup)
            return response

    def put_log_lines(self, log_group, lines, log_stream_name=None):
        """
        Put this lines in a log group.

        :param log_stream_name:
        :param log_group: Log group with region set.
        :param lines: list of strings to put
        :return:
        """

        events = [{"timestamp": int(datetime.datetime.now().timestamp() * 1000),
                   "message": line
                   } for line in lines]
        if log_stream_name is None:
            log_stream_name = str(uuid.uuid4())
            log_stream_create_request = {"logGroupName": log_group.name,
                                         "logStreamName": log_stream_name}
            self.create_log_stream_raw(log_group.region, log_stream_create_request)
        dict_request = {"logGroupName": log_group.name,
                        "logStreamName": log_stream_name,
                        "logEvents": events
                        }
        return self.put_log_events_raw(log_group.region, dict_request)

    def put_log_events_raw(self, region, request_dict):
        """
        Standard.
        assert ret.get("rejectedLogEventsInfo") is None

        :param request_dict:
        :return:
        """

        logger.info(f"Writing log events: '{request_dict}'")
        for response in self.execute(
                self.get_session_client(region=region).put_log_events, None, raw_data=True, filters_req=request_dict
        ):
            return response

    # pylint: disable= arguments-differ
    def get_tags(self, obj):
        """
        Get tags

        :param obj:
        :return:
        """
        arn = obj.arn
        if arn.endswith(":*"):
            # WHY? Because AWS has f*ng bug!!! They end "insights" ARN with ":*" FFFFFFK
            # pylint: disable= unsubscriptable-object
            arn = obj.arn[:-2]

        request = {"resourceArn": arn}
        tags = list(self.execute(self.get_session_client(region=obj.region).list_tags_for_resource, "tags",
                                 filters_req=request))

        if tags != [{}]:
            obj.tags = tags

    def create_log_stream_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Creating log stream: '{request_dict}'")
        for response in self.execute(
                self.get_session_client(region=region).create_log_stream, None, raw_data=True, filters_req=request_dict
        ):
            return response

    def dispose_log_group(self, log_group):
        """
        Standard.

        :param log_group:
        :return:
        """

        request_dict = {"logGroupName": log_group.name}
        logger.info(f"Disposing log group: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=log_group.region).delete_log_group,
                None,
                raw_data=True,
                filters_req=request_dict,
                exception_ignore_callback=lambda error: "ResourceNotFoundException" in repr(error)
        ):
            self.clear_cache(CloudWatchLogGroup)
            return response
