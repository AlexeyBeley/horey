"""
Testing alert system functions.

"""

import pytest

from horey.alert_system.postgres.postgres_alert_manager import PostgresAlertManager
from horey.alert_system.postgres.postgres_alert_manager_configuration_policy import PostgresAlertManagerConfigurationPolicy
from horey.alert_system.postgres.postgres_cluster_writer_monitoring_configuration_policy import PostgresClusterWriterMonitoringConfigurationPolicy
from horey.alert_system.postgres.postgres_cluster_monitoring_configuration_policy import PostgresClusterMonitoringConfigurationPolicy
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


@pytest.mark.wip
def test_provision_cluster_writer_cpu_utilization(alert_system_configuration):
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
    cluster_writer_config.network_throughput = {"value": 2000, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.read_iops = {"value": 1, "comparison_operator": "GreaterThanThreshold"}

    cluster_writer_config.read_throughput = {"value": 1, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.serverless_database_capacity = {"value": 1, "comparison_operator": "GreaterThanThreshold"}
    cluster_writer_config.maximum_used_transaction_ids = {"value": 2146483648/2, "comparison_operator": "GreaterThanThreshold"}


    alert_system = AlertSystem(alert_system_configuration)
    alerts_manager = PostgresAlertManager(alert_system, configuration, cluster_writer_configuration=cluster_writer_config)
    assert alerts_manager.provision()
