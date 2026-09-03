"""
Monitor mysql like a boss!
"""
import json
from horey.common_utils.common_utils import CommonUtils
from horey.aws_api.aws_services_entities.rds_db_cluster import RDSDBCluster
from horey.aws_api.aws_services_entities.cloud_watch_alarm import CloudWatchAlarm
from horey.h_logger import get_logger
from statistics import median, mean

logger = get_logger()


class ServerlessAlertBuilder:
    """
    Provision
    """

    # pylint: disable = too-many-arguments
    def __init__(self, cache):
        self.cache = cache

    def generate_metric_filters(self):
        """
        Metrics used to monitor the cluster.

        :return:
        """

        ret = []

        dimensions = [
            {"Name": "clusterId", "Value": self.cache.name},
        ]

        ret.append(
            {"Namespace": "AWS/ElastiCache",
             "Dimensions": dimensions})

        return ret

    def generate_metric_alarm_limits(self, metric, statistics_data):
        """
        Generate alarm value min and max.

        :param statistics_data:
        :param metric_raw:
        :return:
        """
        
        min_multiplier = 0.01
        max_multiplier = 10.0

        median_max = median(x["Maximum"] for x in statistics_data)
        mean_max = mean(x["Maximum"] for x in statistics_data)
        absolute_max_value = max(x["Maximum"] for x in statistics_data)

        median_min = median(x["Minimum"] for x in statistics_data)
        mean_min = mean(x["Minimum"] for x in statistics_data)
        absolute_min_value = min(x["Minimum"] for x in statistics_data)

        median_average = median(x["Average"] for x in statistics_data)
        mean_average = mean(x["Average"] for x in statistics_data)
        absolute_min_average = min(x["Average"] for x in statistics_data)
        
        match metric.name:
            case "NewConnections":
                return absolute_min_value, absolute_max_value*max_multiplier
            case "NetworkBytesIn" | "NetworkBytesOut" | "NonKeyTypeCmdsECPUs" | "NonKeyTypeCmds":
                return absolute_min_value * min_multiplier, absolute_max_value * max_multiplier
            case "AuthenticationFailures":
                return None, absolute_max_value
            case "Reclaimed" | "CacheHitRate" | "DB0AverageTTL":
                return absolute_min_value * min_multiplier or None, absolute_max_value * max_multiplier or None
            case "TotalCmdsCount" | "ElastiCacheProcessingUnits" | "BytesUsedForCache":
                return absolute_min_value, absolute_max_value * max_multiplier
            case "CurrConnections":
                return median_min * min_multiplier, absolute_max_value * max_multiplier
            case "ChannelAuthorizationFailures":
                return None, 0
            case _:
                logger.info(f"{metric.name=}, {absolute_min_value=}, {absolute_max_value=}, {median_min=}, {mean_min=}, {median_max=}, {mean_max=}, {median_average=}, {mean_average=}")
                breakpoint()
                return absolute_min_value, absolute_max_value

    def generate_metric_alarm_slug(self, metric):
        """
        camel_case_to_snake_case

        :param metric_raw:
        :return:
        """

        dimension_names_to_values = {x["Name"]: x["Value"] for x in metric.dimensions}
        prefix = ""

        for key in ["clusterId"]:
            if key in dimension_names_to_values:
                prefix += dimension_names_to_values[key] + "_"
                del dimension_names_to_values[key]

        if dimension_names_to_values:
            raise NotImplementedError(f"Not all dimensions handled: {metric.dimensions=}, {dimension_names_to_values=}")

        if not prefix:
            raise NotImplementedError(f"Can not generate unique slug for metric: {metric.dict_src}")

        snake_case = CommonUtils.camel_case_to_snake_case(metric.name)

        return prefix + snake_case 
