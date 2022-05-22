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

#grafana_api = GrafanaAPI(configuration=configuration)


@pytest.mark.skip(reason="Can not test")
def test_init_grafana_api():
    grafana_api = GrafanaAPI(configuration=configuration)
    assert isinstance(grafana_api, GrafanaAPI)

def test_create_dashboard():
    dashboard = Dashboard({
        "cells": [
            {
                "x": 5,
                "y": 5,
                "w": 4,
                "h": 4,
                "name": "usage_user",
                "queries": [],
                "type": "line"
            },
            {
                "x": 0,
                "y": 0,
                "w": 4,
                "h": 4,
                "name": "usage_system",
                "queries": [],
                "type": "line"
            }
        ],
        "name": "lalalalala"
    })
    grafana_api.provision_dashboard(dashboard)
    assert len(grafana_api.rules) > 0


# endregion


if __name__ == "__main__":
    test_init_grafana_api()
    # test_init_kapacitors()
    #test_init_rules()
    #test_create_dashboard()
