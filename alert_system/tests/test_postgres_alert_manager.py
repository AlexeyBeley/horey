"""
Testing alert system functions.

"""

import pytest

from horey.alert_system.postgres.postgres_alert_manager import PostgresAlertManager
from horey.alert_system.postgres.postgres_alert_manager_configuration_policy import PostgresAlertManagerConfigurationPolicy
from horey.alert_system.postgres.postgres_cluster_writer_monitoring_configuration_policy import PostgresClusterWriterMonitoringConfigurationPolicy
from horey.alert_system.postgres.postgres_cluster_monitoring_configuration_policy import PostgresClusterMonitoringConfigurationPolicy
from horey.alert_system.postgres.postgres_instance_monitoring_configuration_policy import PostgresInstanceMonitoringConfigurationPolicy
from horey.alert_system.alert_system import AlertSystem
from horey.alert_system.lambda_package.notification import Notification


# pylint: disable=missing-function-docstring

test_cluster_name = ""


@pytest.mark.done
def test_convert_api_keys_to_snake_case():
    """
    Test provisioning alert_system lambda.

    @return:
    """
    alerts_manager = PostgresAlertManager(None, None)
    ret = alerts_manager.convert_api_keys_to_snake_case()
    print(ret)
    assert ret


@pytest.mark.done
def test_convert_api_keys_to_properties_cluster_metric_names_single_dimension():
    """
    Test provisioning alert_system lambda.

    @return:
    """
    alerts_manager = PostgresAlertManager(None, None)
    ret = alerts_manager.convert_api_keys_to_properties(alerts_manager.cluster_metric_names_single_dimension)
    print(ret)
    assert ret


@pytest.mark.done
def test_convert_api_keys_to_properties_cluster_metric_names_with_role_writer_dimension():
    """
    Test provisioning alert_system lambda.

    @return:
    """
    alerts_manager = PostgresAlertManager(None, None)
    ret = alerts_manager.convert_api_keys_to_properties(alerts_manager.cluster_metric_names_with_role_writer_dimension)
    print(ret)
    assert ret


@pytest.mark.done
def test_get_instance_metric_names(alert_system_configuration):
    """
    Test provisioning alert_system lambda.

    @return:
    """
    alert_system = AlertSystem(alert_system_configuration)
    metrics = alert_system.aws_api.cloud_watch_client.yield_client_metrics(alert_system.region)
    rds_metrics = [metric for metric in metrics if metric["Namespace"] == "AWS/RDS"]
    instance_metrics = [metric for metric in rds_metrics if "instance-aurora-postgres-demo-us-0" in str(metric["Dimensions"])]
    assert len(instance_metrics) == 33


@pytest.mark.done
def test_convert_api_keys_to_properties_instance_metric_names():
    """
    Test provisioning alert_system lambda.

    @return:
    """
    alerts_manager = PostgresAlertManager(None, None)
    ret = alerts_manager.convert_api_keys_to_properties(alerts_manager.instance_metric_names)
    print(ret)
    assert ret


@pytest.mark.done
def test_provision_empty():
    """
    Test provisioning alert_system lambda.

    @return:
    """
    configuration = PostgresAlertManagerConfigurationPolicy()
    alerts_manager = PostgresAlertManager(None, configuration)
    assert alerts_manager.provision()


@pytest.mark.todo
def test_provision_cpuload(alert_system_configuration):
    """
    Test provisioning alert_system lambda.

    @return:
    """
    configuration = PostgresAlertManagerConfigurationPolicy()
    configuration.cluster = test_cluster_name
    alert_system = AlertSystem(alert_system_configuration)
    alerts_manager = PostgresAlertManager(alert_system, configuration)
    assert alerts_manager.provision()


@pytest.mark.done
def test_provision_cluster_writer_monitoring(alert_system_configuration):
    """
    Test provisioning alert_system lambda.

    @return:
    """

    configuration = PostgresAlertManagerConfigurationPolicy()
    configuration.cluster = test_cluster_name
    configuration.routing_tags = [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG]
    cluster_writer_config = PostgresClusterWriterMonitoringConfigurationPolicy()
    cluster_writer_config.cpu_utilization = {"value": 80, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.acu_utilization = {"value": 80, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.ebs_byte_balance_percent = {"value": 50, "comparison_operator": "LessThanThreshold"}
    cluster_writer_config.storage_network_receive_throughput = {"value": 4000, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.storage_network_transmit_throughput = {"value": 30000, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.network_throughput = {"value": 2000, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.read_iops = {"value": 1, "comparison_operator": "GreaterThanThreshold"}

    cluster_writer_config.read_throughput = {"value": 1, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.serverless_database_capacity = {"value": 1, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.maximum_used_transaction_ids = {"value": 2146483648/2, "comparison_operator": "GreaterThanThreshold"}

    cluster_writer_config.ebsio_balance_percent= {"value": 50, "comparison_operator": "LessThanThreshold"}
    cluster_writer_config.ebsio_balance_percent= {"value": 50, "comparison_operator": "LessThanThreshold"}
    cluster_writer_config.temp_storage_iops = {"value": 300, "comparison_operator": "GreaterThanThreshold"}

    cluster_writer_config.deadlocks = {"value": 0, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.read_latency = {"value": 0.01, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.disk_queue_depth = {"value": 0, "comparison_operator": "GreaterThanThreshold"}

    cluster_writer_config.network_receive_throughput = {"value": 5000, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.commit_latency = {"value": 30, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.swap_usage = {"value": 400000000, "comparison_operator": "GreaterThanThreshold"}

    cluster_writer_config.storage_network_throughput = {"value": 25000, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.write_latency = {"value": 0.021, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.write_iops = {"value": 6.0, "comparison_operator": "GreaterThanThreshold"}

    cluster_writer_config.write_throughput = {"value": 1190, "comparison_operator": "GreaterThanThreshold"}

    cluster_writer_config.write_throughput = {"value": 1190, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.transaction_logs_disk_usage = {"value": 0, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.oldest_replication_slot_lag = {"value": 0, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.database_connections = {"value": 5, "comparison_operator": "GreaterThanThreshold"}

    cluster_writer_config.rds_to_aurora_postgre_sql_replica_lag = {"value": 0, "comparison_operator": "GreaterThanThreshold"}

    cluster_writer_config.buffer_cache_hit_ratio = {"value": 50, "comparison_operator": "LessThanThreshold"}
    cluster_writer_config.engine_uptime = {"value": 1500000, "comparison_operator": "GreaterThanThreshold"}

    cluster_writer_config.commit_throughput = {"value": 4, "comparison_operator": "GreaterThanThreshold"}

    cluster_writer_config.temp_storage_throughput = {"value": 1000000, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.network_transmit_throughput = {"value": 1000, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.freeable_memory = {"value": 500000000, "comparison_operator": "LessThanThreshold"}
    cluster_writer_config.replication_slot_disk_usage = {"value": 0, "comparison_operator": "GreaterThanThreshold"}

    alert_system = AlertSystem(alert_system_configuration)
    alerts_manager = PostgresAlertManager(alert_system, configuration, cluster_writer_configuration=cluster_writer_config)
    assert alerts_manager.provision()


@pytest.mark.done
def test_provision_cluster_monitoring(alert_system_configuration):
    """
    Test provisioning alert_system lambda.

    @return:
    """

    configuration = PostgresAlertManagerConfigurationPolicy()
    configuration.cluster = test_cluster_name
    configuration.routing_tags = [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG]

    cluster_config = PostgresClusterMonitoringConfigurationPolicy()
    cluster_config.acu_utilization = {"value": 50.4, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.backup_retention_period_storage_used = {"value": 1000000000, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.buffer_cache_hit_ratio = {"value": 100, "comparison_operator": "LessThanThreshold"}
    cluster_config.commit_latency = {"value": 1, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.commit_throughput = {"value": 4.06, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.cpu_utilization = {"value": 30, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.database_connections = {"value": 3, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.deadlocks = {"value": 0, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.disk_queue_depth = {"value": 0, "comparison_operator": "GreaterThanThreshold"}

    cluster_config.ebs_byte_balance_percent = {"value": 90, "comparison_operator": "LessThanThreshold"}
    cluster_config.ebs_io_balance_percent = {"value": 90, "comparison_operator": "LessThanThreshold"}
    cluster_config.engine_uptime = {"value": 1000000, "comparison_operator": "LessThanThreshold"}
    cluster_config.freeable_memory = {"value": 2000000000, "comparison_operator": "LessThanThreshold"}

    cluster_config.maximum_used_transaction_ids = {"value": 2146483648/2, "comparison_operator": "GreaterThanThreshold"}
    # todo: read about above metric

    cluster_config.network_receive_throughput = {"value": 600, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.network_throughput = {"value": 1000, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.network_transmit_throughput = {"value": 8000, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.oldest_replication_slot_lag = {"value": 0, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.rds_to_aurora_postgre_sql_replica_lag = {"value": 0, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.read_iops = {"value": 0.01, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.read_latency = {"value": 0.01, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.read_throughput = {"value": 10.0, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.replication_slot_disk_usage = {"value": 0, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.serverless_database_capacity = {"value": 1, "comparison_operator": "LessThanThreshold"}

    cluster_config.storage_network_receive_throughput = {"value": 5000, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.storage_network_throughput = {"value": 1000000, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.storage_network_transmit_throughput = {"value": 1000000, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.swap_usage = {"value": 383000000, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.temp_storage_iops = {"value": 150, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.temp_storage_throughput = {"value": 1000000, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.total_backup_storage_billed = {"value": 1000000000, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.transaction_logs_disk_usage = {"value": 0, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.volume_bytes_used = {"value": 200000000, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.volume_read_iops = {"value": 0.5, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.volume_write_iops = {"value": 1500, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.write_iops = {"value": 10, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.write_latency = {"value": 0.01, "comparison_operator": "GreaterThanThreshold"}
    cluster_config.write_throughput = {"value": 5000, "comparison_operator": "GreaterThanThreshold"}


    #####
    alert_system = AlertSystem(alert_system_configuration)
    alerts_manager = PostgresAlertManager(alert_system, configuration, cluster_configuration=cluster_config)
    assert alerts_manager.provision()


@pytest.mark.done
def test_provision_instance_monitoring(alert_system_configuration):
    """
    Test provisioning alert_system lambda.

    @return:
    """

    configuration = PostgresAlertManagerConfigurationPolicy()
    configuration.cluster = test_cluster_name
    configuration.routing_tags = [Notification.ALERT_SYSTEM_SELF_MONITORING_ROUTING_TAG]

    instance_config = PostgresInstanceMonitoringConfigurationPolicy()
    instance_config.deadlocks = {"value": 0, "comparison_operator": "GreaterThanThreshold"}
    instance_config.swap_usage = {"value": 400000000, "comparison_operator": "GreaterThanThreshold"}
    instance_config.temp_storage_throughput = {"value": 1000000, "comparison_operator": "GreaterThanThreshold"}
    instance_config.network_receive_throughput = {"value": 500, "comparison_operator": "GreaterThanThreshold"}
    instance_config.network_throughput = {"value": 600, "comparison_operator": "GreaterThanThreshold"}
    instance_config.freeable_memory = {"value": 2*1024*1024, "comparison_operator": "LessThanThreshold"}
    instance_config.acu_utilization = {"value": 50.4, "comparison_operator": "GreaterThanThreshold"}
    instance_config.serverless_database_capacity = {"value": 1, "comparison_operator": "GreaterThanThreshold"}
    instance_config.maximum_used_transaction_ids = {"value": 2146483648/2, "comparison_operator": "GreaterThanThreshold"}
    instance_config.buffer_cache_hit_ratio = {"value": 90, "comparison_operator": "LessThanThreshold"}
    instance_config.cpu_utilization = {"value": 80, "comparison_operator": "GreaterThanThreshold"}
    instance_config.network_transmit_throughput = {"value": 400, "comparison_operator": "GreaterThanThreshold"}
    instance_config.ebs_io_balance_percent = {"value": 80, "comparison_operator": "LessThanThreshold"}
    instance_config.oldest_replication_slot_lag = {"value": 1, "comparison_operator": "GreaterThanThreshold"}
    instance_config.ebs_byte_balance_percent = {"value": 80, "comparison_operator": "LessThanThreshold"}
    instance_config.storage_network_receive_throughput = {"value": 5000, "comparison_operator": "GreaterThanThreshold"}
    instance_config.disk_queue_depth = {"value": 0, "comparison_operator": "GreaterThanThreshold"}
    instance_config.write_throughput = {"value": 1000, "comparison_operator": "GreaterThanThreshold"}

    instance_config.storage_network_throughput = {"value": 100000, "comparison_operator": "GreaterThanThreshold"}

    instance_config.commit_latency = {"value": 1.5, "comparison_operator": "GreaterThanThreshold"}
    instance_config.commit_throughput = {"value": 4.2, "comparison_operator": "GreaterThanThreshold"}

    ##########
    instance_config.rds_to_aurora_postgre_sql_replica_lag= {"value": 0, "comparison_operator": "GreaterThanThreshold"}
    instance_config.database_connections = {"value": 10, "comparison_operator": "GreaterThanThreshold"}

    instance_config.read_throughput = {"value": 1, "comparison_operator": "GreaterThanThreshold"}
    instance_config.replication_slot_disk_usage = {"value": 0, "comparison_operator": "GreaterThanThreshold"}
    instance_config.write_iops = {"value": 6, "comparison_operator": "GreaterThanThreshold"}
    instance_config.write_latency = {"value": 0.002, "comparison_operator": "GreaterThanThreshold"}

    instance_config.read_latency = {"value": 0.002, "comparison_operator": "GreaterThanThreshold"}
    instance_config.transaction_logs_disk_usage = {"value": 0, "comparison_operator": "GreaterThanThreshold"}
    instance_config.engine_uptime = {"value": 1000000, "comparison_operator": "LessThanThreshold"}
    instance_config.temp_storage_iops = {"value": 150, "comparison_operator": "GreaterThanThreshold"}
    instance_config.read_iops = {"value": 0, "comparison_operator": "GreaterThanThreshold"}
    instance_config.storage_network_transmit_throughput = {"value": 150000, "comparison_operator": "GreaterThanThreshold"}

    #####
    alert_system = AlertSystem(alert_system_configuration)
    alerts_manager = PostgresAlertManager(alert_system, configuration, instance_configuration=instance_config)
    assert alerts_manager.provision()
