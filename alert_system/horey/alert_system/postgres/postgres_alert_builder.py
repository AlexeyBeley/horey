"""
Monitor postgres like a boss!
"""
import json


from horey.aws_api.aws_services_entities.rds_db_cluster import RDSDBCluster
from horey.aws_api.aws_services_entities.cloud_watch_alarm import CloudWatchAlarm
from horey.h_logger import get_logger
from statistics import median, mean

logger = get_logger()


class PostgresAlertBuilder:
    """
    Provision
    """

    # pylint: disable = too-many-arguments
    def __init__(self, cluster=None):
        self.cluster = cluster
        self.camel_case_to_snake_case = {"ServerlessDatabaseCapacity": "serverless_database_capacity",
                                         "BufferCacheHitRatio": "buffer_cache_hit_ratio",
                                         "DiskQueueDepth": "disk_queue_depth",
                                         "DBLoadNonCPU": "db_load_non_cpu",
                                         "ReadIOPSLocalStorage": "read_iops_local_storage",
                                         "ReplicationSlotDiskUsage": "replication_slot_disk_usage",
                                         "VolumeBytesUsed": "volume_bytes_used",
                                         "EngineUptime": "engine_uptime",
                                         "EBSByteBalance%": "ebs_byte_balance_percent",
                                         "NetworkReceiveThroughput": "network_receive_throughput",
                                         "StorageNetworkThroughput": "storage_network_throughput",
                                         "ReplicaLag": "replica_lag",
                                         "FreeStorageSpace": "free_storage_space",
                                         "VolumeReadIOPs": "volume_read_iops",
                                         "Deadlocks": "deadlocks",
                                         "ReadThroughput": "read_throughput",
                                         "ReadIOPS": "read_iops",
                                         "NetworkThroughput": "network_throughput",
                                         "DBLoadCPU": "db_load_cpu",
                                         "ReadLatency": "read_latency",
                                         "RDSToAuroraPostgreSQLReplicaLag": "rds_to_aurora_postgre_sql_replica_lag",
                                         "CheckpointLag": "checkpoint_lag",
                                         "EBSIOBalance%": "ebs_io_balance_percent",
                                         "ACUUtilization": "acu_utilization",
                                         "WriteIOPS": "write_iops",
                                         "MaximumUsedTransactionIDs": "maximum_used_transaction_ids",
                                         "FreeableMemory": "freeable_memory",
                                         "WriteLatency": "write_latency",
                                         "CommitThroughput": "commit_throughput",
                                         "OldestReplicationSlotLag": "oldest_replication_slot_lag",
                                         "ReadLatencyLocalStorage": "read_latency_local_storage",
                                         "DatabaseConnections": "database_connections",
                                         "BackupRetentionPeriodStorageUsed": "backup_retention_period_storage_used",
                                         "NetworkTransmitThroughput": "network_transmit_throughput",
                                         "WriteThroughputLocalStorage": "write_throughput_local_storage",
                                         "DBLoad": "db_load",
                                         "ReadThroughputLocalStorage": "read_throughput_local_storage",
                                         "VolumeWriteIOPs": "volume_write_iops",
                                         "TransactionLogsDiskUsage": "transaction_logs_disk_usage",
                                         "DBLoadRelativeToNumVCPUs": "db_load_relative_to_num_vcpus",
                                         "CommitLatency": "commit_latency",
                                         "TempStorageIOPS": "temp_storage_iops",
                                         "WriteLatencyLocalStorage": "write_latency_local_storage",
                                         "StorageNetworkReceiveThroughput": "storage_network_receive_throughput",
                                         "StorageNetworkTransmitThroughput": "storage_network_transmit_throughput",
                                         "TempStorageThroughput": "temp_storage_throughput",
                                         "WriteThroughput": "write_throughput",
                                         "TransactionLogsGeneration": "transaction_logs_generation",
                                         "SwapUsage": "swap_usage",
                                         "TotalBackupStorageBilled": "total_backup_storage_billed",
                                         "CPUUtilization": "cpu_utilization",
                                         "WriteIOPSLocalStorage": "write_iops_local_storage",
                                         "FreeLocalStorage": "free_local_storage",
                                         "AuroraReplicaLagMinimum": "aurora_replica_lag_minimum",
                                         "AuroraReplicaLag": "aurora_replica_lag",
                                         "AuroraReplicaLagMaximum": "aurora_replica_lag_maximum"
                                         }

        self.cluster_metric_names_with_role_writer_dimension = ["NetworkThroughput",
                                                                "ReadIOPS", "ReadThroughput",
                                                                "ServerlessDatabaseCapacity",
                                                                "MaximumUsedTransactionIDs", "EBSIOBalance%",
                                                                "TempStorageIOPS", "Deadlocks", "ReadLatency",
                                                                "StorageNetworkTransmitThroughput",
                                                                "StorageNetworkReceiveThroughput", "CPUUtilization",
                                                                "DiskQueueDepth", "NetworkReceiveThroughput",
                                                                "CommitLatency", "SwapUsage",
                                                                "StorageNetworkThroughput", "WriteLatency",
                                                                "ACUUtilization", "WriteIOPS",
                                                                "WriteThroughput", "TransactionLogsDiskUsage",
                                                                "OldestReplicationSlotLag", "DatabaseConnections",
                                                                "RDSToAuroraPostgreSQLReplicaLag",
                                                                "BufferCacheHitRatio", "EngineUptime",
                                                                "CommitThroughput", "EBSByteBalance%",
                                                                "TempStorageThroughput", "NetworkTransmitThroughput",
                                                                "FreeableMemory", "ReplicationSlotDiskUsage"]
        self.cluster_metric_names_single_dimension = ["ReadLatency",
                                                      "RDSToAuroraPostgreSQLReplicaLag",
                                                      "DiskQueueDepth",
                                                      "Deadlocks",
                                                      "VolumeWriteIOPs",
                                                      "EBSByteBalance%",
                                                      "FreeableMemory",
                                                      "EngineUptime",
                                                      "SwapUsage",
                                                      "TotalBackupStorageBilled",
                                                      "VolumeBytesUsed",
                                                      "ReadThroughput",
                                                      "CommitLatency",
                                                      "EBSIOBalance%",
                                                      "ReadIOPS",
                                                      "CommitThroughput",
                                                      "WriteThroughput",
                                                      "TempStorageIOPS",
                                                      "BackupRetentionPeriodStorageUsed",
                                                      "TempStorageThroughput",
                                                      "CPUUtilization",
                                                      "DatabaseConnections",
                                                      "StorageNetworkTransmitThroughput",
                                                      "OldestReplicationSlotLag",
                                                      "ServerlessDatabaseCapacity",
                                                      "WriteLatency",
                                                      "WriteIOPS",
                                                      "NetworkTransmitThroughput",
                                                      "StorageNetworkThroughput",
                                                      "TransactionLogsDiskUsage",
                                                      "BufferCacheHitRatio",
                                                      "VolumeReadIOPs",
                                                      "NetworkReceiveThroughput",
                                                      "ACUUtilization",
                                                      "MaximumUsedTransactionIDs",
                                                      "StorageNetworkReceiveThroughput",
                                                      "ReplicationSlotDiskUsage",
                                                      "NetworkThroughput"]
        self.instance_metric_names = ["ReadIOPS", "FreeableMemory", "SwapUsage", "WriteIOPS",
                                      "ServerlessDatabaseCapacity", "DatabaseConnections", "CommitLatency",
                                      "EBSByteBalance%", "NetworkReceiveThroughput", "ReplicationSlotDiskUsage",
                                      "CommitThroughput", "ACUUtilization", "StorageNetworkReceiveThroughput",
                                      "TempStorageThroughput", "MaximumUsedTransactionIDs", "WriteLatency",
                                      "StorageNetworkThroughput", "EngineUptime", "OldestReplicationSlotLag",
                                      "StorageNetworkTransmitThroughput", "NetworkThroughput", "ReadLatency",
                                      "TempStorageIOPS", "CPUUtilization", "RDSToAuroraPostgreSQLReplicaLag",
                                      "Deadlocks", "ReadThroughput", "WriteThroughput", "DiskQueueDepth",
                                      "BufferCacheHitRatio", "NetworkTransmitThroughput", "EBSIOBalance%",
                                      "TransactionLogsDiskUsage"]

    def convert_api_keys_to_snake_case(self):
        """
        Convert from api to configuration

        :return:
        """

        input_keys = ["ServerlessDatabaseCapacity", "BufferCacheHitRatio", "DiskQueueDepth",
                      "DBLoadNonCPU", "ReadIOPSLocalStorage", "ReplicationSlotDiskUsage",
                      "VolumeBytesUsed", "EngineUptime", "EBSByteBalance%",
                      "NetworkReceiveThroughput", "StorageNetworkThroughput", "ReplicaLag",
                      "FreeStorageSpace", "VolumeReadIOPs", "Deadlocks", "ReadThroughput",
                      "ReadIOPS", "NetworkThroughput", "DBLoadCPU", "ReadLatency",
                      "RDSToAuroraPostgreSQLReplicaLag", "CheckpointLag", "EBSIOBalance%",
                      "ACUUtilization", "WriteIOPS", "MaximumUsedTransactionIDs",
                      "FreeableMemory", "WriteLatency", "CommitThroughput",
                      "OldestReplicationSlotLag", "ReadLatencyLocalStorage",
                      "DatabaseConnections", "BackupRetentionPeriodStorageUsed",
                      "NetworkTransmitThroughput", "WriteThroughputLocalStorage", "DBLoad",
                      "ReadThroughputLocalStorage", "VolumeWriteIOPs",
                      "TransactionLogsDiskUsage", "DBLoadRelativeToNumVCPUs", "CommitLatency",
                      "TempStorageIOPS", "WriteLatencyLocalStorage",
                      "StorageNetworkReceiveThroughput", "StorageNetworkTransmitThroughput",
                      "TempStorageThroughput", "WriteThroughput", "TransactionLogsGeneration",
                      "SwapUsage", "TotalBackupStorageBilled", "CPUUtilization",
                      "WriteIOPSLocalStorage", "FreeLocalStorage"]

        str_ret = "{"
        for api_key_name in input_keys:
            snake_case = self.camel_case_to_snake_case[api_key_name]
            str_ret += f'"{api_key_name}": "{snake_case}",\n'
        str_ret += "}"
        return str_ret

    def convert_api_keys_to_properties(self, camel_case_keys):
        """
        Convert from api to configuration

        :return:
        """

        str_ret_attributes = ""
        str_ret_properties = ""
        template = \
            "\n    @property\n" \
            "    def replace_me(self):\n" \
            "        if self._replace_me is None:\n" \
            "            self._replace_me = None\n" \
            "        return self._replace_me\n" \
            "\n" \
            "    @replace_me.setter\n" \
            "    def replace_me(self, value):\n" \
            "        self._replace_me = value\n"

        for api_key_name in camel_case_keys:
            snake_case = self.camel_case_to_snake_case[api_key_name]

            str_ret_attributes += f'        self._{snake_case} = None\n'
            str_ret_properties += template.replace("replace_me", snake_case)

        return str_ret_attributes + str_ret_properties

    def provision(self):
        """
        Provision all alarms according to the config policy values

        :return:
        """

        if self.configuration.cluster is not None:
            cluster = RDSDBCluster({})
            cluster.id = self.configuration.cluster
            cluster.region = self.alert_system.region
            if not self.alert_system.aws_api.rds_client.update_db_cluster_information(cluster):
                raise RuntimeError(f"Cluster {cluster.id} can not be found in region {cluster.region.region_mark}")
            self.provision_cluster_writer_alarms()
            self.provision_cluster_alarms()
            self.provision_instance_alarms()
        return True

    def provision_cluster_writer_alarms(self):
        """
        Generate and provision alarms based on configuration

        :return:
        """

        if self.cluster_writer_configuration is None:
            return True

        alarms_counter = 0
        for camel_case in self.cluster_metric_names_with_role_writer_dimension:
            snake_case = self.camel_case_to_snake_case[camel_case]
            metric_config = getattr(self.cluster_writer_configuration, snake_case)
            if metric_config is None:
                continue
            alarm = CloudWatchAlarm({})
            alarm.name = f"{self.alert_system.configuration.lambda_name}-{snake_case}_cluster_writer"
            alarm.actions_enabled = True
            alarm.insufficient_data_actions = []
            alarm.metric_name = camel_case
            alarm.namespace = "AWS/RDS"
            alarm.statistic = "Average"
            alarm.dimensions = [
                {"Name": "DBClusterIdentifier", "Value": self.configuration.cluster},
                {"Name": "Role", "Value": "WRITER"},
            ]
            alarm.period = 60
            alarm.evaluation_periods = 3
            alarm.datapoints_to_alarm = 3
            alarm.threshold = metric_config["value"]
            alarm.comparison_operator = metric_config["comparison_operator"]
            alarm.treat_missing_data = "notBreaching"

            alarm_description = {"routing_tags": self.configuration.routing_tags}
            alarm.alarm_description = json.dumps(alarm_description)
            self.alert_system.provision_cloudwatch_alarm(alarm)
            alarms_counter += 1
        logger.info(f"Provisioned {alarms_counter} cluster alarms")
        return True

    def provision_cluster_alarms(self):
        """
        Generate and provision alarms based on configuration

        :return:
        """

        if self.cluster_configuration is None:
            return True

        alarms_counter = 0
        for camel_case in self.cluster_metric_names_single_dimension:
            snake_case = self.camel_case_to_snake_case[camel_case]
            metric_config = getattr(self.cluster_configuration, snake_case)
            if metric_config is None:
                continue
            alarm = CloudWatchAlarm({})
            alarm.name = f"{self.alert_system.configuration.lambda_name}-{snake_case}_cluster"
            alarm.actions_enabled = True
            alarm.insufficient_data_actions = []
            alarm.metric_name = camel_case
            alarm.namespace = "AWS/RDS"
            alarm.statistic = "Average"
            alarm.dimensions = [
                {"Name": "DBClusterIdentifier", "Value": self.configuration.cluster},
            ]
            alarm.period = 60
            alarm.evaluation_periods = 3
            alarm.datapoints_to_alarm = 3
            alarm.threshold = metric_config["value"]
            alarm.comparison_operator = metric_config["comparison_operator"]
            alarm.treat_missing_data = "notBreaching"

            alarm_description = {"routing_tags": self.configuration.routing_tags}
            alarm.alarm_description = json.dumps(alarm_description)
            self.alert_system.provision_cloudwatch_alarm(alarm)
            alarms_counter += 1
        logger.info(f"Provisioned {alarms_counter} cluster alarms")

        return True

    def provision_instance_alarms(self):
        """
        Generate and provision alarms based on configuration

        :return:
        """

        if self.instance_configuration is None:
            return True

        filters_req = {"Filters": [{"Name": "db-cluster-id", "Values": [self.configuration.cluster]}]}
        instances = list(self.alert_system.aws_api.rds_client.yield_db_instances(region=self.alert_system.region,
                                                                                 filters_req=filters_req))
        if len(instances) != 1:
            raise NotImplementedError(f"{filters_req=}, {self.alert_system.region=}, {len(instances)=}!=1")
        instance_id = instances[0].id
        alarms_counter = 0
        for camel_case in self.instance_metric_names:
            snake_case = self.camel_case_to_snake_case[camel_case]
            metric_config = getattr(self.instance_configuration, snake_case)
            if metric_config is None:
                continue
            alarm = CloudWatchAlarm({})
            alarm.name = f"{self.alert_system.configuration.lambda_name}-{snake_case}_instance"
            alarm.actions_enabled = True
            alarm.insufficient_data_actions = []
            alarm.metric_name = camel_case
            alarm.namespace = "AWS/RDS"
            alarm.statistic = "Average"
            alarm.dimensions = [
                {"Name": "DBInstanceIdentifier", "Value": instance_id}
            ]
            alarm.period = 60
            alarm.evaluation_periods = 3
            alarm.datapoints_to_alarm = 3
            alarm.threshold = metric_config["value"]
            alarm.comparison_operator = metric_config["comparison_operator"]
            alarm.treat_missing_data = "notBreaching"

            alarm_description = {"routing_tags": self.configuration.routing_tags}
            alarm.alarm_description = json.dumps(alarm_description)
            self.alert_system.provision_cloudwatch_alarm(alarm)
            alarms_counter += 1

        logger.info(f"Provisioned {alarms_counter} instance alarms")

        return True

    def generate_cluster_metric_filters(self):
        """
        Metrics used to monitor the cluster.

        :param cluster:
        :return:
        """

        ret = []

        dimensions = [
            {"Name": "DBClusterIdentifier", "Value": self.cluster.id},
        ]

        ret.append(
            {"Namespace": "AWS/RDS",
             "Dimensions": dimensions})

        dimensions = [
            {"Name": "DBClusterIdentifier", "Value": self.cluster.id},
            {"Name": "Role", "Value": "WRITER"},
        ]

        ret.append(
            {"Namespace": "AWS/RDS",
             "Dimensions": dimensions})

        dimensions = [
            {"Name": "DBClusterIdentifier", "Value": self.cluster.id},
            {"Name": "Role", "Value": "READER"},
        ]

        ret.append(
            {"Namespace": "AWS/RDS",
             "Dimensions": dimensions})

        for instance in self.cluster.db_cluster_members:
            ret.append(
                {"Namespace": "AWS/RDS",
                 "Dimensions": [
                     {"Name": "DBInstanceIdentifier", "Value": instance["DBInstanceIdentifier"]}
                 ]})
        return ret

    def generate_metric_alarm_limits(self, metric_raw, statistics_data):
        """
        Generate alarm value min and max.

        :param statistics_data:
        :param metric_raw:
        :return:
        """

        median_max = median(x["Maximum"] for x in statistics_data)
        mean_max = mean(x["Maximum"] for x in statistics_data)
        absolute_max_value = max(x["Maximum"] for x in statistics_data)

        median_min = median(x["Minimum"] for x in statistics_data)
        mean_min = mean(x["Minimum"] for x in statistics_data)
        absolute_min_value = min(x["Minimum"] for x in statistics_data)

        median_average = median(x["Average"] for x in statistics_data)
        mean_average = mean(x["Average"] for x in statistics_data)
        absolute_min_average = min(x["Average"] for x in statistics_data)

        if metric_raw["MetricName"] == "DiskQueueDepth":
            return None, absolute_max_value

        if metric_raw["MetricName"] == "VolumeWriteIOPs":
            return absolute_min_value, min(mean_max * 1.2, absolute_max_value)

        if metric_raw["MetricName"] in ["StorageNetworkThroughput"]:
            ret_min = min(mean_min, median_min)*0.8
            ret_max = max(mean_max, median_max)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["NetworkThroughput"]:
            ret_min = min(mean_average, median_average)*0.8
            ret_max = max(mean_max, median_max)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["ReplicationSlotDiskUsage"]:
            if absolute_min_value != -1.0:
                raise NotImplementedError(f"{absolute_min_value=}")
            if absolute_max_value != -1.0:
                raise NotImplementedError(f"{absolute_max_value=}")
            return None, None

        if metric_raw["MetricName"] in ["Deadlocks"]:
            return None, 0.0

        if metric_raw["MetricName"] in ["BackupRetentionPeriodStorageUsed"]:
            ret_min = min([x for x in [median_min, mean_min, absolute_min_value] if x])*0.8
            ret_max = max(median_max, mean_max, absolute_max_value)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["DiskQueueDepth"]:
            breakpoint()
            ret_min = min([x for x in [median_min, mean_min, absolute_min_value] if x])*0.8
            ret_max = max(median_max, mean_max, absolute_max_value)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["VolumeReadIOPs"]:
            ret_min = ret_max = None
            if (median_max, mean_max, absolute_max_value) != (0.0, 0.0, 0.0):
                ret_max = max(median_max, mean_max)*1.2
            if (median_min, mean_min, absolute_min_value) != (0.0, 0.0, 0.0):
                ret_min = min([x for x in [median_min, mean_min, absolute_min_value] if x]) * 0.8
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["ReadIOPS"]:
            ret_max = None
            ret_min = None
            if (median_max, mean_max, absolute_max_value) != (0.0, 0.0, 0.0):
                ret_max = max(mean_max, median_max)*1.2
            if median_min != 0.0:
                ret_min = min(mean_min, median_min)*0.8
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["ACUUtilization"]:
            return 30, 80

        if metric_raw["MetricName"] in ["TempStorageIOPS"]:
            ret_min = min(median_min, mean_min) * 0.8
            ret_max = max(median_max, mean_max) * 1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["ServerlessDatabaseCapacity"]:
            return float(self.cluster.serverless_v2_scaling_configuration["MinCapacity"])*1.2, \
                float(self.cluster.serverless_v2_scaling_configuration["MaxCapacity"])*0.8

        if metric_raw["MetricName"] in ["RDSToAuroraPostgreSQLReplicaLag"]:
            if (median_max, mean_max, absolute_max_value) != (-1.0, -1.0, -1.0):
                raise NotImplementedError(median_max, mean_max, absolute_max_value)
            if (median_min, mean_min, absolute_min_value) != (-1.0, -1.0, -1.0):
                raise NotImplementedError(median_min, mean_min, absolute_min_value)
            return None, None

        if metric_raw["MetricName"] in ["StorageNetworkTransmitThroughput"]:
            ret_min = min(median_min, mean_min) * 0.8
            ret_max = max(median_max, mean_max) * 1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["CPUUtilization"]:
            return 5, 90

        if metric_raw["MetricName"] in ["AuroraReplicaLagMinimum"]:
            ret_min = min(median_min, mean_min) * 0.8
            ret_max = max(median_max, mean_max) * 1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["WriteThroughput"]:
            ret_min = min(mean_min, median_min)*0.8
            ret_max = max(mean_max, median_max)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["WriteLatency"]:
            ret_min = min(mean_average, median_average)*0.8
            ret_max = max(mean_max, median_max)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["CommitThroughput"]:
            ret_min = min(mean_min, median_min)*0.8
            ret_max = max(mean_max, median_max)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["NetworkTransmitThroughput"]:
            ret_min = min(mean_average, median_average)*0.8
            ret_max = max(mean_max, median_max)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["MaximumUsedTransactionIDs"]:
            ret_min = min(mean_min, median_min)*0.8
            ret_max = max(mean_max, median_max)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["EngineUptime"]:
            ret_min = 60.0
            ret_max = 60.0*60*24*30*12
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["EBSByteBalance%"]:
            ret_min = 80.0
            return ret_min, None

        if metric_raw["MetricName"] in ["WriteIOPS"]:
            ret_min = min(mean_min, median_min)*0.8
            ret_max = max(mean_max, median_max)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["CommitLatency"]:
            ret_min = min(mean_min, median_min)*0.8
            ret_max = max(mean_max, median_max)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["FreeableMemory"]:
            ret_min = min(mean_min, median_min)*0.8
            ret_max = max(mean_max, median_max)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["TempStorageThroughput"]:
            ret_min = min(mean_min, median_min)*0.8
            ret_max = max(mean_max, median_max)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["EBSIOBalance%"]:
            ret_min = 80.0
            return ret_min, None

        if metric_raw["MetricName"] in ["SwapUsage"]:
            ret_min = min(mean_min, median_min)*0.8
            ret_max = max(mean_max, median_max)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["DatabaseConnections"]:
            ret_min = min(mean_min, median_min)*0.8
            ret_max = max(mean_max, median_max)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["TransactionLogsDiskUsage"]:
            if (median_max, mean_max, absolute_max_value) != (-1.0, -1.0, -1.0):
                raise NotImplementedError(median_max, mean_max, absolute_max_value)
            if (median_min, mean_min, absolute_min_value) != (-1.0, -1.0, -1.0):
                raise NotImplementedError(median_min, mean_min, absolute_min_value)
            return None, None

        if metric_raw["MetricName"] in ["BufferCacheHitRatio"]:
            return 80, None

        if metric_raw["MetricName"] in ["VolumeBytesUsed"]:
            ret_min = min(mean_min, median_min)*0.8
            ret_max = max(mean_max, median_max)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["ReadThroughput"]:
            ret_max = None
            ret_min = None
            if (median_max, mean_max, absolute_max_value) != (0.0, 0.0, 0.0):
                ret_max = max(mean_max, median_max)*1.2
            if median_min != 0.0:
                ret_min = min(mean_min, median_min)*0.8
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["OldestReplicationSlotLag"]:
            if (median_max, mean_max, absolute_max_value) != (0.0, 0.0, 0.0):
                raise NotImplementedError(median_max, mean_max, absolute_max_value)
            if (median_min, mean_min, absolute_min_value) != (0.0, 0.0, 0.0):
                raise NotImplementedError(median_min, mean_min, absolute_min_value)
            return None, None

        if metric_raw["MetricName"] in ["TotalBackupStorageBilled"]:
            ret_min = min(mean_min, median_min)*0.8
            ret_max = max(mean_max, median_max)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["ReadLatency"]:
            ret_max = None
            ret_min = None
            if (median_max, mean_max, absolute_max_value) != (0.0, 0.0, 0.0):
                ret_max = max(mean_max, median_max)*1.2
            if median_min != 0.0:
                ret_min = min(mean_min, median_min)*0.8
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["StorageNetworkReceiveThroughput"]:
            ret_min = min(mean_min, median_min)*0.8
            ret_max = max(mean_max, median_max)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["NetworkReceiveThroughput"]:
            # min is 0.0, 0.0, 0.0
            ret_min = min(mean_average, median_average)*0.8
            ret_max = max(mean_max, median_max)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["AuroraReplicaLag"]:
            ret_min = min(mean_average, median_average)*0.8
            ret_max = max(mean_max, median_max)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["AuroraReplicaLagMaximum"]:
            ret_min = min(mean_min, median_min)*0.8
            ret_max = max(mean_max, median_max)*1.2
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["DBLoadNonCPU"]:
            if (median_max, mean_max, absolute_max_value) != (0.0, 0.0, 0.0):
                raise NotImplementedError(median_max, mean_max, absolute_max_value)
            if (median_min, mean_min, absolute_min_value) != (0.0, 0.0, 0.0):
                raise NotImplementedError(median_min, mean_min, absolute_min_value)
            return None, None

        if metric_raw["MetricName"] in ["DBLoad"]:
            ret_min = None
            ret_max = max(mean_max, median_max) * 1.2
            if median_min != 0.0:
                raise NotImplementedError(median_min, mean_min, absolute_min_value)
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["DBLoadRelativeToNumVCPUs"]:
            ret_min = None
            ret_max = max(mean_max, median_max) * 1.2
            if median_min != 0.0:
                raise NotImplementedError(median_min, mean_min, absolute_min_value)
            return ret_min, ret_max

        if metric_raw["MetricName"] in ["DBLoadCPU"]:
            ret_min = None
            ret_max = max(mean_max, median_max) * 1.2
            if median_min != 0.0:
                raise NotImplementedError(median_min, mean_min, absolute_min_value)
            return ret_min, ret_max

        breakpoint()
        return absolute_min_value, absolute_max_value

        median_max, mean_max, absolute_max_value
        median_min, mean_min, absolute_min_value
        median_average, mean_average, absolute_min_average

    def generate_metric_alarm_slug(self, metric_raw):
        """
        camel_case_to_snake_case

        :param metric_raw:
        :return:
        """

        dimension_names_to_values = {x["Name"]: x["Value"] for x in metric_raw["Dimensions"]}
        prefix = ""

        for key in ["DBClusterIdentifier", "Role", "DBInstanceIdentifier"]:
            if key in dimension_names_to_values:
                prefix += dimension_names_to_values[key] + "_"
                del dimension_names_to_values[key]

        if dimension_names_to_values:
            raise NotImplementedError(f"Not all dimensions handled: {metric_raw=}, {dimension_names_to_values=}")

        if not prefix:
            raise NotImplementedError(f"Can not generate unique slug for metric: {metric_raw}")

        return prefix + self.camel_case_to_snake_case[metric_raw["MetricName"]]
