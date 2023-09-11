"""
AWS client to handle cloud watch entities
"""

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.cloud_watch_alarm import CloudWatchAlarm
from horey.aws_api.aws_services_entities.cloud_watch_metric import CloudWatchMetric
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.h_logger import get_logger

logger = get_logger()




class CloudWatchClient(Boto3Client):
    """
    Client to work with cloud watch entities API
    """

    def __init__(self):
        client_name = "cloudwatch"
        super().__init__(client_name)

    def yield_cloud_watch_metrics(self):
        """
        Yields metrics - made to handle large amounts of data, in order to prevent the OOM collapse.
        :return:
        """
        for region in AWSAccount.get_aws_account().regions.values():
            AWSAccount.set_aws_region(region)
            for response in self.execute(self.client.list_metrics, "Metrics"):
                yield response

    def yield_client_metrics(self, filters_req=None):
        """
        Generator for standard region fetcher

        :param filters_req:
        :return:
        """
        for response in self.execute(self.client.list_metrics, "Metrics", filters_req=filters_req):
            yield response

    def get_all_metrics(self, update_info=False):
        """
        Get all metrics

        :return:
        """

        regional_fetcher_generator = self.yield_client_metrics
        return list(self.regional_service_entities_generator(regional_fetcher_generator, CloudWatchMetric, update_info=update_info))

    def get_all_alarms(self, update_info=False):
        """
        Get all alarms in all regions.

        :return:
        """

        regional_fetcher_generator = self.regional_fetcher_generator_alarms
        return list(self.regional_service_entities_generator(regional_fetcher_generator, CloudWatchAlarm, update_info=update_info))

    def regional_fetcher_generator_alarms(self, filters_req=None):
        """
        Generator. Yield over the fetched alarms.

        :return:
        """


        for dict_src in self.execute(self.client.describe_alarms, None, raw_data=True, filters_req=filters_req):
            if len(dict_src["CompositeAlarms"]) != 0:
                raise NotImplementedError("CompositeAlarms")
            for dict_alarm in dict_src["MetricAlarms"]:
                yield dict_alarm

    def set_cloudwatch_alarm(self, alarm):
        """
        Provision alarm.

        :param alarm:
        :return:
        """

        request_dict = alarm.generate_create_request()
        AWSAccount.set_aws_region(alarm.region)
        logger.info(
            f"Creating cloudwatch alarm '{alarm.name}' in region '{alarm.region}'"
        )
        for response in self.execute(
            self.client.put_metric_alarm, "ResponseMetadata", filters_req=request_dict
        ):
            if response["HTTPStatusCode"] != 200:
                raise RuntimeError(f"{response}")
