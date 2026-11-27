"""
Monitor opensearch like a boss!
"""
from statistics import median, mean

from horey.common_utils.common_utils import CommonUtils
from horey.h_logger import get_logger

logger = get_logger()


class OpensearchAlertBuilder:
    """
    Generate CloudWatch alarm limits and slugs for an Opensearch domain.
    """

    NAMESPACE = "AWS/ES"

    # Metrics whose healthy value is always zero: any sustained non-zero value is an alert.
    ZERO_TOLERANCE_METRICS = ["5xx",
                              "AutomatedSnapshotFailure",
                              "ClusterIndexWritesBlocked",
                              "KMSKeyError",
                              "KMSKeyInaccessible",
                              "ThreadpoolSearchRejected",
                              "ThreadpoolWriteRejected",
                              "ThreadpoolIndexRejected"]

    def __init__(self, domain):
        self.domain = domain

    @property
    def account_id(self):
        """
        Account id is a mandatory "ClientId" dimension of all the domain metrics.
        ARN format: arn:aws:es:<region>:<account_id>:domain/<name>

        :return:
        """

        return self.domain.arn.split(":")[4]

    def generate_cluster_metric_filters(self):
        """
        Metrics used to monitor the domain.

        :return:
        """

        dimensions = [
            {"Name": "DomainName", "Value": self.domain.name},
            {"Name": "ClientId", "Value": self.account_id},
        ]

        return [{"Namespace": self.NAMESPACE,
                 "Dimensions": dimensions}]

    # pylint: disable = too-many-return-statements
    def generate_metric_alarm_limits(self, metric_raw, statistics_data):
        """
        Generate alarm value min and max.
        None means no alarm for the boundary.

        :param statistics_data:
        :param metric_raw:
        :return:
        """

        metric_name = metric_raw["MetricName"]

        if not statistics_data:
            logger.warning(f"No datapoints for metric: {metric_name}")
            return None, None

        min_multiplier = 0.01
        max_multiplier = 10.0

        median_max = median(x["Maximum"] for x in statistics_data)
        mean_max = mean(x["Maximum"] for x in statistics_data)

        median_min = median(x["Minimum"] for x in statistics_data)
        mean_min = mean(x["Minimum"] for x in statistics_data)
        absolute_min_value = min(x["Minimum"] for x in statistics_data)

        if metric_name in self.ZERO_TOLERANCE_METRICS:
            return None, 0.0

        # 1 - the status is active, 0 - it is not.
        if metric_name == "ClusterStatus.red":
            return None, 0.5

        if metric_name == "ClusterStatus.green":
            # Single data node domains with replicas are always yellow - nothing to monitor then.
            if absolute_min_value < 1.0:
                return None, None
            return 0.5, None

        # Covered by ClusterStatus.green
        if metric_name == "ClusterStatus.yellow":
            return None, None

        if metric_name == "Nodes":
            return min(mean_min, median_min), None

        if metric_name in ["CPUUtilization", "MasterCPUUtilization"]:
            return None, 90.0

        if metric_name in ["JVMMemoryPressure", "MasterJVMMemoryPressure"]:
            return None, 95.0

        if metric_name == "FreeStorageSpace":
            # Megabytes. 20 GiB, but never above half of the usual free space of a small domain.
            return min(20 * 1024.0, median_min * 0.5), None

        ret_min = ret_max = None
        if (median_min, mean_min) != (0.0, 0.0):
            ret_min = min(mean_min, median_min) * min_multiplier
        if (median_max, mean_max) != (0.0, 0.0):
            ret_max = max(mean_max, median_max) * max_multiplier

        logger.info(f"Implicit metric: {metric_name}, {ret_min=}, {ret_max=}")
        return ret_min, ret_max

    def generate_metric_alarm_slug(self, metric_raw):
        """
        Unique alarm slug per domain and metric.

        :param metric_raw:
        :return:
        """

        dimension_names_to_values = {x["Name"]: x["Value"] for x in metric_raw["Dimensions"]}

        if dimension_names_to_values.pop("DomainName", None) != self.domain.name:
            raise NotImplementedError(f"Metric does not belong to the domain {self.domain.name}: {metric_raw=}")

        dimension_names_to_values.pop("ClientId", None)

        if dimension_names_to_values:
            raise NotImplementedError(f"Not all dimensions handled: {metric_raw=}, {dimension_names_to_values=}")

        snake_case = CommonUtils.camel_case_to_snake_case(metric_raw["MetricName"]).replace(".", "_")

        return f"{self.domain.name}_{snake_case}"
