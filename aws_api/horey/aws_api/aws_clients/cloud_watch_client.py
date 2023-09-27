"""
AWS client to handle cloud watch logs.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.cloud_watch_alarm import CloudWatchAlarm
from horey.aws_api.aws_services_entities.cloud_watch_metric import CloudWatchMetric
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.h_logger import get_logger

logger = get_logger()


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

    def get_region_metrics(self, region):
        """
        Get region metrics

        :return:
        """

        AWSAccount.set_aws_region(region)
        ret = []
        for response in self.execute(self.client.list_metrics, "Metrics"):
            obj = CloudWatchMetric(response)
            ret.append(obj)
        return ret

    def get_all_alarms(self):
        """
        Get all alarms in all regions.
        :return:
        """
        final_result = []

        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_alarms(region)

        return final_result

    def get_region_alarms(self, region):
        """
        Get all alarms in the region.

        :return:
        """

        AWSAccount.set_aws_region(region)
        final_result = []

        for dict_src in self.execute(self.client.describe_alarms, None, raw_data=True):
            if len(dict_src["CompositeAlarms"]) != 0:
                raise NotImplementedError("CompositeAlarms")
            for dict_alarm in dict_src["MetricAlarms"]:
                alarm = CloudWatchAlarm(dict_alarm)
                alarm.region = AWSAccount.get_aws_region()
                final_result.append(alarm)

        return final_result

    def set_cloudwatch_alarm(self, alarm):
        """
        Standard.

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

    def put_metric_data_raw(self, request_dict):
        """
        {Namespace:'string',
            MetricData:[]
        }

        :param request_dict:
        :return:
        """

        logger.info(f"Putting metric data: {request_dict}")

        for response in self.execute(
                self.client.put_metric_data,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            del response["ResponseMetadata"]
            return response

    def get_metric_data_raw(self, request_dict):
        """
        Fetch metric data.

        :param request_dict:
        :return:
        """

        logger.info(f"Getting metric data: {request_dict}")

        return list(self.execute(
                self.client.get_metric_data,
                "MetricDataResults",
                raw_data=True,
                filters_req=request_dict,
        ))

    def set_alarm_state_raw(self, request_dict):
        """
          AlarmName='string',
          StateValue='OK'|'ALARM'|'INSUFFICIENT_DATA',
          StateReason='string',

        :param request_dict:
        :return:
        """

        logger.info(f"Setting alarm state: {request_dict}")

        for response in self.execute(
                self.client.set_alarm_state,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            del response["ResponseMetadata"]
            return response
