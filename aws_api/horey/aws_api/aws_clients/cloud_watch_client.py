"""
AWS client to handle cloud watch logs.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.cloud_watch_alarm import CloudWatchAlarm
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.h_logger import get_logger

logger = get_logger()


import pdb
class CloudWatchClient(Boto3Client):
    """
    Client to work with cloud watch logs API.
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

    def get_cloud_watch_alarms(self):
        """
        Get all alarms in all regions.
        :return:
        """
        final_result = list()

        for region in AWSAccount.get_aws_account().regions.values():
            AWSAccount.set_aws_region(region)
            for dict_src in self.execute(self.client.describe_alarms, None, raw_data=True):
                if len(dict_src["CompositeAlarms"]) != 0:
                    raise NotImplementedError("CompositeAlarms")
                for dict_alarm in dict_src["MetricAlarms"]:
                    alarm = CloudWatchAlarm(dict_alarm)
                    alarm.region = AWSAccount.get_aws_region()
                    final_result.append(alarm)

        return final_result

    def set_cloudwatch_alarm(self, alarm):
        request_dict = alarm.generate_create_request()
        AWSAccount.set_aws_region(alarm.region)
        logger.info(f"Creating cloudwatch alarm '{alarm.name}' in region '{alarm.region}'")
        for response in self.execute(self.client.put_metric_alarm, "ResponseMetadata", filters_req=request_dict):
            if response["HTTPStatusCode"] != 200:
                raise RuntimeError(f"{response}")