"""
Monitor postgres like a boss!
"""
from horey.common_utils.common_utils import CommonUtils
from horey.alert_system.postgres.postgres_alert_manager_configuration_policy import \
    PostgresAlertManagerConfigurationPolicy
from horey.alert_system.alert_system import AlertSystem
from horey.aws_api.aws_services_entities.rds_db_cluster import RDSDBCluster


class PostgresAlertManager:
    """
    Provision
    """

    def __init__(self, alert_system: AlertSystem, configuration: PostgresAlertManagerConfigurationPolicy):
        self.alert_system = alert_system
        self.configuration = configuration
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
                                         "VolumeReadIOPs": "volume_read_io_ps",
                                         "Deadlocks": "deadlocks",
                                         "ReadThroughput": "read_throughput",
                                         "ReadIOPS": "read_iops",
                                         "NetworkThroughput": "network_throughput",
                                         "DBLoadCPU": "db_load_cpu",
                                         "ReadLatency": "read_latency",
                                         "RDSToAuroraPostgreSQLReplicaLag": "rds_to_aurora_postgre_sql_replica_lag",
                                         "CheckpointLag": "checkpoint_lag",
                                         "EBSIOBalance%": "ebsio_balance_percent",
                                         "ACUUtilization": "acu_utilization",
                                         "WriteIOPS": "write_iops",
                                         "MaximumUsedTransactionIDs": "maximum_used_transaction_i_ds",
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
                                         "VolumeWriteIOPs": "volume_write_io_ps",
                                         "TransactionLogsDiskUsage": "transaction_logs_disk_usage",
                                         "DBLoadRelativeToNumVCPUs": "db_load_relative_to_num_vcp_us",
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
                                         }

        self.cluster_metric_names_with_role_writer_dimension = ["VolumeReadIOPs", "NetworkThroughput", "VolumeBytesUsed", "ReadIOPS", "ReadThroughput", "ServerlessDatabaseCapacity", "MaximumUsedTransactionIDs", "EBSIOBalance%", "TempStorageIOPS", "Deadlocks", "ReadLatency", "StorageNetworkTransmitThroughput", "StorageNetworkReceiveThroughput", "CPUUtilization", "DiskQueueDepth", "NetworkReceiveThroughput", "CommitLatency", "SwapUsage", "StorageNetworkThroughput", "WriteLatency", "VolumeWriteIOPs", "ACUUtilization", "WriteIOPS", "WriteThroughput", "TransactionLogsDiskUsage", "OldestReplicationSlotLag", "DatabaseConnections", "RDSToAuroraPostgreSQLReplicaLag", "BufferCacheHitRatio", "EngineUptime", "CommitThroughput", "EBSByteBalance%", "TempStorageThroughput", "NetworkTransmitThroughput", "FreeableMemory", "ReplicationSlotDiskUsage"]
        self.cluster_metric_names_single_dimension = ['ReadLatency', 'RDSToAuroraPostgreSQLReplicaLag', 'DiskQueueDepth',
                                             'Deadlocks', 'VolumeWriteIOPs', 'EBSByteBalance%', 'FreeableMemory',
                                             'EngineUptime', 'SwapUsage', 'TotalBackupStorageBilled', 'VolumeBytesUsed',
                                             'ReadThroughput', 'CommitLatency', 'EBSIOBalance%', 'ReadIOPS',
                                             'CommitThroughput', 'WriteThroughput', 'TempStorageIOPS',
                                             'BackupRetentionPeriodStorageUsed', 'TempStorageThroughput',
                                             'CPUUtilization', 'DatabaseConnections',
                                             'StorageNetworkTransmitThroughput', 'OldestReplicationSlotLag',
                                             'ServerlessDatabaseCapacity', 'WriteLatency', 'WriteIOPS',
                                             'NetworkTransmitThroughput', 'StorageNetworkThroughput',
                                             'TransactionLogsDiskUsage', 'BufferCacheHitRatio', 'VolumeReadIOPs',
                                             'NetworkReceiveThroughput', 'ACUUtilization', 'MaximumUsedTransactionIDs',
                                             'StorageNetworkReceiveThroughput', 'ReplicationSlotDiskUsage',
                                             'NetworkThroughput']

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
            snake_case = self.convert_camel_case_to_snake_case(api_key_name)
            str_ret += f'"{api_key_name}": "{snake_case}",\n'
        str_ret += "}"
        return str_ret

    @staticmethod
    def convert_camel_case_to_snake_case(str_src):
        """
        Transform camel case to snake case and remove all extra chars

        :return:
        """

        return CommonUtils.camel_case_to_snake_case(str_src).replace("%", "_percent")

    def convert_api_keys_to_properties(self):
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

        str_ret = ""
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

        for api_key_name in input_keys:
            snake_case = self.convert_camel_case_to_snake_case(api_key_name)
            str_ret += f'        self._{snake_case} = None\n'

        for api_key_name in input_keys:
            snake_case = self.convert_camel_case_to_snake_case(api_key_name)
            str_ret += template.replace("replace_me", snake_case)

        return str_ret

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
            if not self.alert_system.aws_api.rds_client.update_cluster_full_information(cluster):
                raise RuntimeError(f"Cluster {cluster.id} can not be found in region {cluster.region.region_mark}")
            self.provision_cluster_writer_alarms(cluster)
        instance_metric_names = ['WriteThroughput', 'ReadIOPS', 'ReadLatency', 'NetworkTransmitThroughput',
                                 'ReadThroughput', 'StorageNetworkReceiveThroughput', 'EBSIOBalance%',
                                 'TransactionLogsDiskUsage', 'CommitThroughput', 'ACUUtilization', 'EngineUptime',
                                 'NetworkReceiveThroughput', 'FreeableMemory', 'ServerlessDatabaseCapacity',
                                 'MaximumUsedTransactionIDs', 'WriteIOPS', 'EBSByteBalance%', 'DatabaseConnections',
                                 'StorageNetworkThroughput', 'WriteLatency', 'SwapUsage', 'NetworkThroughput',
                                 'ReplicationSlotDiskUsage', 'TempStorageIOPS', 'OldestReplicationSlotLag',
                                 'CommitLatency', 'RDSToAuroraPostgreSQLReplicaLag', 'TempStorageThroughput',
                                 'Deadlocks', 'DiskQueueDepth', 'CPUUtilization', 'BufferCacheHitRatio',
                                 'StorageNetworkTransmitThroughput']


        return True

    def provision_cluster_writer_alarms(self, cluster):
        breakpoint()
        for camel_case, snake_case in self.camel_case_to_snake_case.items():
            snake_case += "_cluster_writer"
            if camel_case not in cluster_metric_names_with_role_writer_dimension:
                continue
            if getattr(self.configuration, snake_case) is not None:
                breakpoint()

    def provision_cluster_alarms(self, cluster):
        breakpoint()