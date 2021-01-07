"""
AWS client to handle cloud watch logs.
"""
from boto3_client import Boto3Client
from cloud_watch_log_group import CloudWatchLogGroup


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

        for result in self.execute(self.client.describe_log_groups, "logGroups"):
            obj = CloudWatchLogGroup(result)
            if full_information:
                self.update_log_group_full_information(obj)

            final_result.append(obj)
        return final_result

    def update_log_group_full_information(self, obj):
        """
        Fetches and updates obj
        :param obj:
        :return: None, raise if fails
        """

        for response in self.execute(self.client.describe_log_streams, "logStreams", filters_req={"logGroupName": obj.name}):
            obj.update_log_stream(response)

    def yield_log_group_streams(self, log_group_name):
        """
        Yields streams - made to handle large log groups, in order to prevent the OOM collapse.
        :param log_group_name:
        :return:
        """
        for response in self.execute(self.client.describe_log_streams, "logStreams", filters_req={"logGroupName": log_group_name}):
            yield response
