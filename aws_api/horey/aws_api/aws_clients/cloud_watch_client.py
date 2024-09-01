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
            yield from self.execute(self.get_session_client(region=region).list_metrics, "Metrics")

    def yield_client_metrics(self, region, filters_req=None):
        """
        Generator for standard region fetcher

        :param filters_req:
        :return:
        """
        yield from self.execute(self.get_session_client(region=region).list_metrics, "Metrics",
                                     filters_req=filters_req)

    def get_all_metrics(self, update_info=False):
        """
        Get all metrics

        :return:
        """

        regional_fetcher_generator = self.yield_client_metrics
        return list(self.regional_service_entities_generator(regional_fetcher_generator, CloudWatchMetric,
                                                             update_info=update_info))

    def get_all_alarms(self, update_info=False):
        """
        Get all alarms in all regions.

        :return:
        """

        regional_fetcher_generator = self.regional_fetcher_generator_alarms
        return list(self.regional_service_entities_generator(regional_fetcher_generator, CloudWatchAlarm,
                                                             update_info=update_info))

    def regional_fetcher_generator_alarms(self, region, filters_req=None):
        """
        Generator. Yield over the fetched alarms.

        :return:
        """

        for dict_src in self.execute(self.get_session_client(region=region).describe_alarms, None, raw_data=True,
                                     filters_req=filters_req):
            if len(dict_src["CompositeAlarms"]) != 0:
                raise NotImplementedError("CompositeAlarms")
            yield from dict_src["MetricAlarms"]

    def set_cloudwatch_alarm(self, alarm: CloudWatchAlarm):
        """
        Provision alarm.

        :param alarm:
        :return:
        """

        request_dict = alarm.generate_create_request()
        logger.info(
            f"Creating cloudwatch alarm '{alarm.name}' in region '{alarm.region}'"
        )
        for response in self.execute(
                self.get_session_client(region=alarm.region).put_metric_alarm, "ResponseMetadata",
                filters_req=request_dict
        ):
            if response["HTTPStatusCode"] != 200:
                raise RuntimeError(f"{response}")

        alarms_by_name = list(self.regional_fetcher_generator_alarms(alarm.region, filters_req={"AlarmNames": [alarm.name]}))
        if len(alarms_by_name) != 1:
            raise RuntimeError(f"Was not able to find single alarm by name '{alarm.name}' in region '{alarm.region.region_mark}'")

        alarm.update_from_raw_response(alarms_by_name[0])

    def put_metric_data_raw(self, region, request_dict):
        """
        {Namespace:'string',
            MetricData:[]
        }

        :param request_dict:
        :return:
        """

        logger.info(f"Putting metric data: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).put_metric_data,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            del response["ResponseMetadata"]
            return response

    def get_metric_data_raw(self, region, request_dict):
        """
        Fetch metric data.

        :param request_dict:
        :return:
        """

        logger.info(f"Getting metric data: {request_dict}")

        return list(self.execute(
            self.get_session_client(region=region).get_metric_data,
            "MetricDataResults",
            raw_data=True,
            filters_req=request_dict,
        ))

    def set_alarm_state_raw(self, region, request_dict):
        """
          AlarmName='string',
          StateValue='OK'|'ALARM'|'INSUFFICIENT_DATA',
          StateReason='string',

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Setting alarm state: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).set_alarm_state,
                None,
                raw_data=True,
                filters_req=request_dict,
                instant_raise=True
        ):
            return response

    def set_alarm_ok(self, alarm):
        """
        Change the alarm state.

        :param alarm:
        :return:
        """

        dict_request = {"AlarmName": alarm.name,
                        "StateValue": "OK",
                        "StateReason": "Explicitly changed state to OK"}

        return self.set_alarm_state_raw(alarm.region, dict_request)
