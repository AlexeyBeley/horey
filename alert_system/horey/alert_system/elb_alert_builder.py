"""
Monitor postgres like a boss!
"""

from horey.h_logger import get_logger
from statistics import median, mean
from horey.common_utils.common_utils import CommonUtils

logger = get_logger()


class ELBAlertBuilder:
    """
    Provision
    """

    # pylint: disable = too-many-arguments
    def __init__(self, load_balancer_name=None):
        self.load_balancer_name = load_balancer_name

    def convert_api_keys_to_snake_case(self, input_keys):
        """
        Convert from api to configuration

        :return:
        """

        str_ret = "{"
        for api_key_name in input_keys:
            snake_case = CommonUtils.camel_case_to_snake_case(api_key_name)
            str_ret += f'"{api_key_name}": "{snake_case}",\n'
        str_ret += "}"
        return str_ret

    def generate_metric_alarm_limits(self, metric_raw, statistics_data):
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

        if metric_raw["MetricName"] == "DesyncMitigationMode_NonCompliant_Request_Count":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier,
                                                 max_multiplier)

        if metric_raw["MetricName"] == "HealthyHostCount":
            ret_min, ret_max = None, None
            if median_max != 0.0:
                ret_max = int(max(median_max, mean_max) * max_multiplier)
            if median_min != 0.0:
                # max(0, 1)
                ret_min = max(int(min(median_min, mean_min) * 0.5), 1)
            return ret_min, ret_max

        if metric_raw["MetricName"] == "HTTPCode_ELB_504_Count":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier,
                                                 max_multiplier)

        if metric_raw["MetricName"] == "NewConnectionCount":
            ret_min, ret_max = None, None
            if median_max != 0.0:
                breakpoint()
            if median_min != 0.0:
                breakpoint()
            return ret_min, ret_max
        if metric_raw["MetricName"] == "ActiveConnectionCount":
            ret_min, ret_max = None, None
            if median_max != 0.0:
                breakpoint()
            if median_min != 0.0:
                breakpoint()
            return ret_min, ret_max

        if metric_raw["MetricName"] == "HealthyStateDNS":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier,
                                                 max_multiplier)

        if metric_raw["MetricName"] == "RequestCount":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier,
                                                 max_multiplier)

        if metric_raw["MetricName"] == "UnhealthyStateDNS":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier,
                                                 max_multiplier)

        if metric_raw["MetricName"] == "ForwardedInvalidHeaderRequestCount":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier,
                                                 max_multiplier)

        if metric_raw["MetricName"] == "RuleEvaluations":
            ret_min, ret_max = None, None
            if median_max != 0.0:
                breakpoint()
            if median_min != 0.0:
                breakpoint()
            return ret_min, ret_max
        if metric_raw["MetricName"] == "UnHealthyHostCount":
            ret_min, ret_max = None, None
            if median_max != 0.0:
                breakpoint()
            if median_min != 0.0:
                breakpoint()
            return ret_min, ret_max

        if metric_raw["MetricName"] == "HTTPCode_ELB_3XX_Count":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier, max_multiplier)

        if metric_raw["MetricName"] == "HTTPCode_Target_2XX_Count":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier, max_multiplier)

        if metric_raw["MetricName"] == "PeakLCUs":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier, max_multiplier)

        if metric_raw["MetricName"] == "MitigatedHostCount":
            ret_min, ret_max = None, None
            if median_max != 0.0:
                breakpoint()
            if median_min != 0.0:
                breakpoint()
            return ret_min, ret_max

        if metric_raw["MetricName"] == "HTTPCode_ELB_5XX_Count":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier, max_multiplier)

        if metric_raw["MetricName"] == "HTTPCode_Target_5XX_Count":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier, max_multiplier)

        if metric_raw["MetricName"] == "ConsumedLCUs":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier, max_multiplier)

        if metric_raw["MetricName"] == "RequestCountPerTarget":
            ret_min, ret_max = None, None
            if median_max != 0.0:
                breakpoint()
            if median_min != 0.0:
                breakpoint()
            return ret_min, ret_max
        if metric_raw["MetricName"] == "ProcessedBytes":
            ret_min, ret_max = None, None
            if median_max != 0.0:
                breakpoint()
            if median_min != 0.0:
                breakpoint()
            return ret_min, ret_max

        if metric_raw["MetricName"] == "HTTPCode_Target_3XX_Count":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier,
                                                 max_multiplier)

        if metric_raw["MetricName"] == "HTTP_Redirect_Count":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier,
                                                 max_multiplier)

        if metric_raw["MetricName"] == "UnhealthyStateRouting":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier,
                                                 max_multiplier)

        if metric_raw["MetricName"] == "HealthyStateRouting":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier,
                                                 max_multiplier)

        if metric_raw["MetricName"] == "LambdaTargetProcessedBytes":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier,
                                                 max_multiplier)

        if metric_raw["MetricName"] == "HTTPCode_ELB_4XX_Count":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier,
                                                 max_multiplier)

        if metric_raw["MetricName"] == "HTTPCode_Target_4XX_Count":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier,
                                                 max_multiplier)

        if metric_raw["MetricName"] == "AnomalousHostCount":
            ret_min, ret_max = None, None
            if median_max != 0.0:
                breakpoint()
            if median_min != 0.0:
                breakpoint()
            return ret_min, ret_max

        if metric_raw["MetricName"] == "ClientTLSNegotiationErrorCount":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier,
                                                 max_multiplier)

        if metric_raw["MetricName"] == "TargetResponseTime":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier,
                                                 max_multiplier)

        if metric_raw["MetricName"] == "UnhealthyRoutingRequestCount":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier,
                                                 max_multiplier)

        if metric_raw["MetricName"] == "HTTPCode_ELB_502_Count":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier,
                                                 max_multiplier)

        if metric_raw["MetricName"] == "LambdaUserError":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier,
                                                 max_multiplier)

        if metric_raw["MetricName"] == "TargetTLSNegotiationErrorCount":
            return self.generate_standard_limits(median_min, mean_min, median_max, mean_max, min_multiplier,
                                                 max_multiplier)
        breakpoint()
        return absolute_min_value, absolute_max_value

        median_max, mean_max, absolute_max_value
        median_min, mean_min, absolute_min_value
        median_average, mean_average, absolute_min_average

    def generate_standard_limits(self, median_min, mean_min, median_max, mean_max, min_multiplier, max_multiplier):
        """
        Standard calculus

        :param median_min:
        :param mean_min:
        :param median_max:
        :param mean_max:
        :param min_multiplier:
        :param max_multiplier:
        :return:
        """

        ret_min, ret_max = None, None
        if median_max != 0.0:
            ret_max = max(median_max, mean_max) * max_multiplier
        if median_min != 0.0:
            ret_min = min(median_min, mean_min) * min_multiplier
        return ret_min, ret_max

    def generate_metric_alarm_slug(self, metric_raw):
        """
        Generate slug used in alarm name

        :param metric_raw:
        :return:
        """

        dimension_names_to_values = {x["Name"]: x["Value"] for x in metric_raw["Dimensions"]}
        prefix = ""

        for key in ["LoadBalancer", "TargetGroup", "AvailabilityZone"]:
            if key in dimension_names_to_values:
                prefix += dimension_names_to_values[key] + "_"
                del dimension_names_to_values[key]

        if dimension_names_to_values:
            raise NotImplementedError(f"Not all dimensions handled: {metric_raw=}, {dimension_names_to_values=}")

        if not prefix:
            raise NotImplementedError(f"Can not generate unique slug for metric: {metric_raw}")

        return prefix + CommonUtils.camel_case_to_snake_case(metric_raw["MetricName"])

    def filter_metrics(self, metrics):
        """
        Filter relevant metrics

        :param metrics:
        :return:
        """

        lst_ret = []
        for metric in metrics:
            if metric["Namespace"] != "AWS/ApplicationELB":
                continue
            if self.load_balancer_name not in str(metric):
                continue
            lst_ret.append(metric)
        return lst_ret
