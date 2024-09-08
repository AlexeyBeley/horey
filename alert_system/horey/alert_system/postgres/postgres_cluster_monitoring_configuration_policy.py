"""
Postgres Alert Manager configuration policy.

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable=missing-function-docstring


class PostgresClusterMonitoringConfigurationPolicy(ConfigurationPolicy):
    """
    Main class.
    """

    def __init__(self):
        super().__init__()
        self._read_latency = None
        self._rds_to_aurora_postgre_sql_replica_lag = None
        self._disk_queue_depth = None
        self._deadlocks = None
        self._volume_write_io_ps = None
        self._ebs_byte_balance_percent = None
        self._freeable_memory = None
        self._engine_uptime = None
        self._swap_usage = None
        self._total_backup_storage_billed = None
        self._volume_bytes_used = None
        self._read_throughput = None
        self._commit_latency = None
        self._ebsio_balance_percent = None
        self._read_iops = None
        self._commit_throughput = None
        self._write_throughput = None
        self._temp_storage_iops = None
        self._backup_retention_period_storage_used = None
        self._temp_storage_throughput = None
        self._cpu_utilization = None
        self._database_connections = None
        self._storage_network_transmit_throughput = None
        self._oldest_replication_slot_lag = None
        self._serverless_database_capacity = None
        self._write_latency = None
        self._write_iops = None
        self._network_transmit_throughput = None
        self._storage_network_throughput = None
        self._transaction_logs_disk_usage = None
        self._buffer_cache_hit_ratio = None
        self._volume_read_io_ps = None
        self._network_receive_throughput = None
        self._acu_utilization = None
        self._maximum_used_transaction_ids = None
        self._storage_network_receive_throughput = None
        self._replication_slot_disk_usage = None
        self._network_throughput = None

    @property
    def read_latency(self):
        if self._read_latency is None:
            self._read_latency = None
        return self._read_latency

    @read_latency.setter
    def read_latency(self, value):
        self._read_latency = value

    @property
    def rds_to_aurora_postgre_sql_replica_lag(self):
        if self._rds_to_aurora_postgre_sql_replica_lag is None:
            self._rds_to_aurora_postgre_sql_replica_lag = None
        return self._rds_to_aurora_postgre_sql_replica_lag

    @rds_to_aurora_postgre_sql_replica_lag.setter
    def rds_to_aurora_postgre_sql_replica_lag(self, value):
        self._rds_to_aurora_postgre_sql_replica_lag = value

    @property
    def disk_queue_depth(self):
        if self._disk_queue_depth is None:
            self._disk_queue_depth = None
        return self._disk_queue_depth

    @disk_queue_depth.setter
    def disk_queue_depth(self, value):
        self._disk_queue_depth = value

    @property
    def deadlocks(self):
        if self._deadlocks is None:
            self._deadlocks = None
        return self._deadlocks

    @deadlocks.setter
    def deadlocks(self, value):
        self._deadlocks = value

    @property
    def volume_write_io_ps(self):
        if self._volume_write_io_ps is None:
            self._volume_write_io_ps = None
        return self._volume_write_io_ps

    @volume_write_io_ps.setter
    def volume_write_io_ps(self, value):
        self._volume_write_io_ps = value

    @property
    def ebs_byte_balance_percent(self):
        if self._ebs_byte_balance_percent is None:
            self._ebs_byte_balance_percent = None
        return self._ebs_byte_balance_percent

    @ebs_byte_balance_percent.setter
    def ebs_byte_balance_percent(self, value):
        self._ebs_byte_balance_percent = value

    @property
    def freeable_memory(self):
        if self._freeable_memory is None:
            self._freeable_memory = None
        return self._freeable_memory

    @freeable_memory.setter
    def freeable_memory(self, value):
        self._freeable_memory = value

    @property
    def engine_uptime(self):
        if self._engine_uptime is None:
            self._engine_uptime = None
        return self._engine_uptime

    @engine_uptime.setter
    def engine_uptime(self, value):
        self._engine_uptime = value

    @property
    def swap_usage(self):
        if self._swap_usage is None:
            self._swap_usage = None
        return self._swap_usage

    @swap_usage.setter
    def swap_usage(self, value):
        self._swap_usage = value

    @property
    def total_backup_storage_billed(self):
        if self._total_backup_storage_billed is None:
            self._total_backup_storage_billed = None
        return self._total_backup_storage_billed

    @total_backup_storage_billed.setter
    def total_backup_storage_billed(self, value):
        self._total_backup_storage_billed = value

    @property
    def volume_bytes_used(self):
        if self._volume_bytes_used is None:
            self._volume_bytes_used = None
        return self._volume_bytes_used

    @volume_bytes_used.setter
    def volume_bytes_used(self, value):
        self._volume_bytes_used = value

    @property
    def read_throughput(self):
        if self._read_throughput is None:
            self._read_throughput = None
        return self._read_throughput

    @read_throughput.setter
    def read_throughput(self, value):
        self._read_throughput = value

    @property
    def commit_latency(self):
        if self._commit_latency is None:
            self._commit_latency = None
        return self._commit_latency

    @commit_latency.setter
    def commit_latency(self, value):
        self._commit_latency = value

    @property
    def ebsio_balance_percent(self):
        if self._ebsio_balance_percent is None:
            self._ebsio_balance_percent = None
        return self._ebsio_balance_percent

    @ebsio_balance_percent.setter
    def ebsio_balance_percent(self, value):
        self._ebsio_balance_percent = value

    @property
    def read_iops(self):
        if self._read_iops is None:
            self._read_iops = None
        return self._read_iops

    @read_iops.setter
    def read_iops(self, value):
        self._read_iops = value

    @property
    def commit_throughput(self):
        if self._commit_throughput is None:
            self._commit_throughput = None
        return self._commit_throughput

    @commit_throughput.setter
    def commit_throughput(self, value):
        self._commit_throughput = value

    @property
    def write_throughput(self):
        if self._write_throughput is None:
            self._write_throughput = None
        return self._write_throughput

    @write_throughput.setter
    def write_throughput(self, value):
        self._write_throughput = value

    @property
    def temp_storage_iops(self):
        if self._temp_storage_iops is None:
            self._temp_storage_iops = None
        return self._temp_storage_iops

    @temp_storage_iops.setter
    def temp_storage_iops(self, value):
        self._temp_storage_iops = value

    @property
    def backup_retention_period_storage_used(self):
        if self._backup_retention_period_storage_used is None:
            self._backup_retention_period_storage_used = None
        return self._backup_retention_period_storage_used

    @backup_retention_period_storage_used.setter
    def backup_retention_period_storage_used(self, value):
        self._backup_retention_period_storage_used = value

    @property
    def temp_storage_throughput(self):
        if self._temp_storage_throughput is None:
            self._temp_storage_throughput = None
        return self._temp_storage_throughput

    @temp_storage_throughput.setter
    def temp_storage_throughput(self, value):
        self._temp_storage_throughput = value

    @property
    def cpu_utilization(self):
        if self._cpu_utilization is None:
            self._cpu_utilization = None
        return self._cpu_utilization

    @cpu_utilization.setter
    def cpu_utilization(self, value):
        self._cpu_utilization = value

    @property
    def database_connections(self):
        if self._database_connections is None:
            self._database_connections = None
        return self._database_connections

    @database_connections.setter
    def database_connections(self, value):
        self._database_connections = value

    @property
    def storage_network_transmit_throughput(self):
        if self._storage_network_transmit_throughput is None:
            self._storage_network_transmit_throughput = None
        return self._storage_network_transmit_throughput

    @storage_network_transmit_throughput.setter
    def storage_network_transmit_throughput(self, value):
        self._storage_network_transmit_throughput = value

    @property
    def oldest_replication_slot_lag(self):
        if self._oldest_replication_slot_lag is None:
            self._oldest_replication_slot_lag = None
        return self._oldest_replication_slot_lag

    @oldest_replication_slot_lag.setter
    def oldest_replication_slot_lag(self, value):
        self._oldest_replication_slot_lag = value

    @property
    def serverless_database_capacity(self):
        if self._serverless_database_capacity is None:
            self._serverless_database_capacity = None
        return self._serverless_database_capacity

    @serverless_database_capacity.setter
    def serverless_database_capacity(self, value):
        self._serverless_database_capacity = value

    @property
    def write_latency(self):
        if self._write_latency is None:
            self._write_latency = None
        return self._write_latency

    @write_latency.setter
    def write_latency(self, value):
        self._write_latency = value

    @property
    def write_iops(self):
        if self._write_iops is None:
            self._write_iops = None
        return self._write_iops

    @write_iops.setter
    def write_iops(self, value):
        self._write_iops = value

    @property
    def network_transmit_throughput(self):
        if self._network_transmit_throughput is None:
            self._network_transmit_throughput = None
        return self._network_transmit_throughput

    @network_transmit_throughput.setter
    def network_transmit_throughput(self, value):
        self._network_transmit_throughput = value

    @property
    def storage_network_throughput(self):
        if self._storage_network_throughput is None:
            self._storage_network_throughput = None
        return self._storage_network_throughput

    @storage_network_throughput.setter
    def storage_network_throughput(self, value):
        self._storage_network_throughput = value

    @property
    def transaction_logs_disk_usage(self):
        if self._transaction_logs_disk_usage is None:
            self._transaction_logs_disk_usage = None
        return self._transaction_logs_disk_usage

    @transaction_logs_disk_usage.setter
    def transaction_logs_disk_usage(self, value):
        self._transaction_logs_disk_usage = value

    @property
    def buffer_cache_hit_ratio(self):
        if self._buffer_cache_hit_ratio is None:
            self._buffer_cache_hit_ratio = None
        return self._buffer_cache_hit_ratio

    @buffer_cache_hit_ratio.setter
    def buffer_cache_hit_ratio(self, value):
        self._buffer_cache_hit_ratio = value

    @property
    def volume_read_io_ps(self):
        if self._volume_read_io_ps is None:
            self._volume_read_io_ps = None
        return self._volume_read_io_ps

    @volume_read_io_ps.setter
    def volume_read_io_ps(self, value):
        self._volume_read_io_ps = value

    @property
    def network_receive_throughput(self):
        if self._network_receive_throughput is None:
            self._network_receive_throughput = None
        return self._network_receive_throughput

    @network_receive_throughput.setter
    def network_receive_throughput(self, value):
        self._network_receive_throughput = value

    @property
    def acu_utilization(self):
        if self._acu_utilization is None:
            self._acu_utilization = None
        return self._acu_utilization

    @acu_utilization.setter
    def acu_utilization(self, value):
        self._acu_utilization = value

    @property
    def maximum_used_transaction_ids(self):
        if self._maximum_used_transaction_ids is None:
            self._maximum_used_transaction_ids = None
        return self._maximum_used_transaction_ids

    @maximum_used_transaction_ids.setter
    def maximum_used_transaction_ids(self, value):
        self._maximum_used_transaction_ids = value

    @property
    def storage_network_receive_throughput(self):
        if self._storage_network_receive_throughput is None:
            self._storage_network_receive_throughput = None
        return self._storage_network_receive_throughput

    @storage_network_receive_throughput.setter
    def storage_network_receive_throughput(self, value):
        self._storage_network_receive_throughput = value

    @property
    def replication_slot_disk_usage(self):
        if self._replication_slot_disk_usage is None:
            self._replication_slot_disk_usage = None
        return self._replication_slot_disk_usage

    @replication_slot_disk_usage.setter
    def replication_slot_disk_usage(self, value):
        self._replication_slot_disk_usage = value

    @property
    def network_throughput(self):
        if self._network_throughput is None:
            self._network_throughput = None
        return self._network_throughput

    @network_throughput.setter
    def network_throughput(self, value):
        self._network_throughput = value