"""
AWS client to handle cloud watch logs.
"""
import pdb

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.cloud_watch_log_group import CloudWatchLogGroup
from horey.aws_api.aws_services_entities.cloud_watch_log_group_metric_filter import CloudWatchLogGroupMetricFilter
from horey.aws_api.base_entities.aws_account import AWSAccount
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

    def get_cloud_watch_log_groups(self, full_information=False):
        """
        Be sure you know what you do, when you set full_information=True.
        This can kill your memory, if you have a lot of data in cloudwatch.
        Better using yield_log_group_streams if you need.

        :param full_information:
        :return:
        """

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_cloud_watch_log_groups(region, full_information=full_information)
        return final_result

    def get_region_cloud_watch_log_groups(self, region, full_information=False):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for result in self.execute(self.client.describe_log_groups, "logGroups"):
            obj = CloudWatchLogGroup(result)
            if full_information:
                self.update_log_group_full_information(obj)

            obj.region = AWSAccount.get_aws_region()
            final_result.append(obj)

        return final_result

    def get_cloud_watch_log_group_metric_filters(self, full_information=False):
        """
        Be sure you know what you do, when you set full_information=True.
        This can kill your memory, if you have a lot of data in cloudwatch.
        Better using yield_log_group_streams if you need.

        :param full_information:
        :return:
        """

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            AWSAccount.set_aws_region(region)
            for result in self.execute(self.client.describe_metric_filters, "metricFilters"):
                obj = CloudWatchLogGroupMetricFilter(result)
                if full_information:
                    self.update_log_group_full_information(obj)

                obj.region = AWSAccount.get_aws_region()
                final_result.append(obj)
        return final_result

    def update_log_group_full_information(self, obj):
        """
        Fetches and updates obj
        :param obj:
        :return: None, raise if fails
        """

        for response in self.execute(self.client.describe_log_streams, "logStreams",
                                     filters_req={"logGroupName": obj.name}):
            obj.update_log_stream(response)

    def yield_log_group_streams(self, log_group):
        """
        Yields streams - made to handle large log groups, in order to prevent the OOM collapse.
        :param log_group:
        :return:
        """
        if AWSAccount.get_aws_region() != log_group.region:
            AWSAccount.set_aws_region(log_group.region)
            
        for response in self.execute(self.client.describe_log_streams, "logStreams",
                                     filters_req={"logGroupName": log_group.name}):
            yield response

    def set_cloudwatch_group_metric_filter(self, metric_filter):
        request_dict = metric_filter.generate_create_request()
        AWSAccount.set_aws_region(metric_filter.region)
        logger.info(f"Creating cloudwatch log group metric filter '{metric_filter.name}' in region '{metric_filter.region}'")
        for response in self.execute(self.client.put_metric_filter, "ResponseMetadata", filters_req=request_dict):
            if response["HTTPStatusCode"] != 200:
                raise RuntimeError(f"{response}")

    def yield_log_events(self, log_group, stream):
        """
        :param log_group:
        :return:
        """
        if AWSAccount.get_aws_region() != log_group.region:
            AWSAccount.set_aws_region(log_group.region)

        self.NEXT_PAGE_RESPONSE_KEY = "nextForwardToken"
        token = None

        for response in self.execute(self.client.get_log_events, "events", raw_data=True,
                                     filters_req={"logGroupName": log_group.name, "logStreamName": stream.name}):
            token = response["nextForwardToken"]
            yield response

        #todo: refactor
        for response in self.execute(self.client.get_log_events, "events", raw_data=True,
                                     filters_req={"logGroupName": log_group.name, "logStreamName": stream.name, "nextToken": token}):
            if token != response["nextForwardToken"]:
                raise ValueError()

    def provision_log_group(self, log_group: CloudWatchLogGroup):
        region_log_groups = self.get_region_cloud_watch_log_groups(log_group.region)
        for region_log_group in region_log_groups:
            if region_log_group.name == log_group.name:
                log_group.update_from_raw_response(region_log_group.dict_src)

        AWSAccount.set_aws_region(log_group.region)
        self.provision_log_group_raw(log_group.generate_create_request())

    def provision_log_group_raw(self, request_dict):
        logger.info(f"Creating log group '{request_dict}'")
        for response in self.execute(self.client.create_log_group, None, raw_data=True, filters_req=request_dict):
            return response
