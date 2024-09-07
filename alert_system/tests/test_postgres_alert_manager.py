"""
Testing alert system functions.

"""

import pytest

from horey.alert_system.postgres.postgres_alert_manager import PostgresAlertManager
from horey.alert_system.postgres.postgres_alert_manager_configuration_policy import PostgresAlertManagerConfigurationPolicy


# pylint: disable=missing-function-docstring


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
def test_convert_api_keys_to_properties():
    """
    Test provisioning alert_system lambda.

    @return:
    """
    alerts_manager = PostgresAlertManager(None, None)
    ret = alerts_manager.convert_api_keys_to_properties()
    print(ret)
    assert ret


@pytest.mark.wip
def test_provision_empty():
    """
    Test provisioning alert_system lambda.

    @return:
    """
    configuration = PostgresAlertManagerConfigurationPolicy()
    alerts_manager = PostgresAlertManager(None, configuration)
    assert alerts_manager.provision()
