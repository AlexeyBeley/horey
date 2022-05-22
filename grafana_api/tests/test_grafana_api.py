import pdb

import pytest
import os

from horey.grafana_api.grafana_api import GrafanaAPI
from horey.grafana_api.grafana_api_configuration_policy import GrafanaAPIConfigurationPolicy
from horey.grafana_api.dashboard import Dashboard

configuration = GrafanaAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                 "grafana_api_configuration_values.py"))
configuration.init_from_file()

grafana_api = GrafanaAPI(configuration=configuration)


@pytest.mark.skip(reason="Can not test")
def test_init_grafana_api():
    grafana_api = GrafanaAPI(configuration=configuration)
    assert isinstance(grafana_api, GrafanaAPI)


@pytest.mark.skip(reason="Can not test")
def test_provision_dashboard():
    dashboard = Dashboard({})
    dashboard.title = "test dashboard1"
    grafana_api.provision_dashboard(dashboard)


@pytest.mark.skip(reason="Can not test")
def test_init_folders_and_dashboards():
    grafana_api.init_folders_and_dashboards()

# endregion


if __name__ == "__main__":
    #test_init_grafana_api()
    #test_provision_dashboard()
    test_init_folders_and_dashboards()
