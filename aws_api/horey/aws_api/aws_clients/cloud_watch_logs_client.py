"""
AWS client to handle cloud watch logs.
"""
import time

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.cloud_watch_log_group import CloudWatchLogGroup
from horey.aws_api.aws_services_entities.cloud_watch_log_group_metric_filter import (
    CloudWatchLogGroupMetricFilter,
)
from horey.aws_api.base_entities.aws_account import AWSAccount
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
        for certificate in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  CloudWatchLogGroup,
                                                  update_info=update_info,
                                                  full_information_callback=None,
                                                  get_tags_callback= get_tags_callback,
                                                  regions=[region] if region else None,
                                                  filters_req=filters_req):
            yield certificate

    def yield_log_groups_raw(self, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """
        for dict_src in self.execute(
                self.client.describe_log_groups, "logGroups", filters_req=filters_req
        ):
            yield dict_src

    def get_cloud_watch_log_groups(self):
        """
        Be sure you know what you do, when you set full_information=True.
        This can kill your memory, if you have a lot of data in cloudwatch.
        Better using yield_log_group_streams_raw if you need.

        :return:
        """

        return list(self.yield_log_groups())

    def get_region_cloud_watch_log_groups(self, region, get_tags=True):
        """
        Get region log groups.

        :param region:
        :param get_tags:
        :return:
        """

        return list(self.yield_log_groups(region=region, get_tags=get_tags))

    def yield_log_group_metric_filters(self, region=None, update_info=False, filters_req=None):
        """
        Yield log_group_metric_filters

        :return:
        """

        regional_fetcher_generator = self.yield_log_group_metric_filters_raw
        for dict_src in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  CloudWatchLogGroupMetricFilter,
                                                  update_info=update_info,
                                                  regions=[region] if region else None,
                                                  filters_req=filters_req):
            yield dict_src

    def yield_log_group_metric_filters_raw(self, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.client.describe_metric_filters, "metricFilters", filters_req=filters_req
        ):
            yield dict_src


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
        if AWSAccount.get_aws_region() != log_group.region:
            AWSAccount.set_aws_region(log_group.region)

        for response in self.execute(
            self.client.describe_log_streams,
            "logStreams",
            filters_req={"logGroupName": log_group.name},
        ):
            yield response

    def yield_log_group_streams(self, log_group):
        """
        Yields streams - made to handle large log groups, in order to prevent the OOM collapse.
        :param log_group:
        :return:
        """
        AWSAccount.set_aws_region(log_group.region)

        for response in self.execute(
            self.client.describe_log_streams,
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
        AWSAccount.set_aws_region(metric_filter.region)
        logger.info(
            f"Creating cloudwatch log group metric filter in region '{metric_filter.region}': {request_dict}"
        )
        for response in self.execute(
            self.client.put_metric_filter, "ResponseMetadata", filters_req=request_dict
        ):
            if response["HTTPStatusCode"] != 200:
                raise RuntimeError(f"{response}")

    def yield_log_events(self, log_group: CloudWatchLogGroup, stream):
        """

        # todo: refactor
        for response in self.execute(
                self.client.get_log_events,
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

        if AWSAccount.get_aws_region() != log_group.region:
            AWSAccount.set_aws_region(log_group.region)

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
                self.client.get_log_events,
                "events",
                raw_data=True,
                filters_req=filters_req,
            ):
                new_token = response["nextForwardToken"]
                logger.info(f"old token: {token} new token: {new_token}")
                if new_token == token:
                    return
                logger.info(f"Extracted {len(response['events'])} events")
                for event in response["events"]:
                    yield event
                time.sleep(10)

            token = new_token
        return

    def provision_log_group(self, log_group: CloudWatchLogGroup):
        """
        Standard.

        :param log_group:
        :return:
        """

        region_log_groups = self.get_region_cloud_watch_log_groups(log_group.region, get_tags=False)
        for region_log_group in region_log_groups:
            if region_log_group.name == log_group.name:
                log_group.update_from_raw_response(region_log_group.dict_src)
                return

        AWSAccount.set_aws_region(log_group.region)
        self.provision_log_group_raw(log_group.generate_create_request())

    def provision_log_group_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Creating log group '{request_dict}'")
        for response in self.execute(
            self.client.create_log_group, None, raw_data=True, filters_req=request_dict
        ):
            return response

    def put_log_events_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Writing log events: '{request_dict}'")
        for response in self.execute(
            self.client.put_log_events, None, raw_data=True, filters_req=request_dict
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
        tags = list(self.execute(self.client.list_tags_for_resource, "tags", filters_req=request))

        if tags != [{}]:
            obj.tags = tags
