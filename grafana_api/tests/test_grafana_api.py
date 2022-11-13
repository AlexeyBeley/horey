"""
Testing grafana API
"""
import os
import json
import pytest

from horey.grafana_api.grafana_api import GrafanaAPI
from horey.grafana_api.grafana_api_configuration_policy import (
    GrafanaAPIConfigurationPolicy,
)
from horey.grafana_api.dashboard import Dashboard


ignore_dir_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore"
)
cache_dir = os.path.join(ignore_dir_path, "grafana_api_cache")
os.makedirs(cache_dir, exist_ok=True)
dashboards_cache_file = os.path.join(cache_dir, "dashboards.json")
folders_cache_file = os.path.join(cache_dir, "folders.json")
rules_cache_file = os.path.join(cache_dir, "rules.json")
dashboards_datasource_file = os.path.join(cache_dir, "datasources.json")

configuration = GrafanaAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(ignore_dir_path, "grafana_api_configuration_values.py")
)
configuration.init_from_file()

grafana_api = GrafanaAPI(configuration=configuration)


@pytest.mark.skip(reason="Can not test")
def test_init_grafana_api():
    """
    Test Grafana API initiation
    @return:
    """
    _grafana_api = GrafanaAPI(configuration=configuration)
    assert isinstance(_grafana_api, GrafanaAPI)


@pytest.mark.skip(reason="Can not test")
def test_provision_dashboard():
    """
    Test dashboard object provisioning
    @return:
    """
    dashboard = Dashboard({})
    dashboard.title = "test dashboard1"
    grafana_api.provision_dashboard(dashboard)


@pytest.mark.skip(reason="Can not test")
def test_create_dashboard_raw():
    """
    Test dashboard creation from raw dict
    @return:
    """
    with open(dashboards_cache_file, encoding="UTF-8") as file_handler:
        dashboards = json.load(file_handler)
    dashboard = dashboards[0]
    request = {
        "dashboard": {
            "id": None,
            "uid": None,
            "title": "test dashboard_copy",
            "tags": ["alexey"],
            "timezone": "browser",
            "schemaVersion": 16,
            "version": 0,
            "refresh": "25s",
            "panels": dashboard["panels"],
        },
        "folderId": None,
        "folderUid": None,
        "message": "Made changes to xyz",
        "overwrite": True,
    }
    grafana_api.create_dashboard_raw(request)


@pytest.mark.skip(reason="Can not test")
def test_create_rule_raw():
    request = {}
    with open(os.path.join(cache_dir, "dashboards.json")) as file_handler:
        pass

    namespace = "critical_alerts"
    grafana_api.create_rule_raw(request, namespace)


@pytest.mark.skip(reason="Can not test")
def test_create_dashboard_generated_raw():
    """
    Test dashboard creation from generated parts.
    @return:
    """
    with open(dashboards_cache_file, encoding="UTF-8") as file_handler:
        dashboards = json.load(file_handler)
    dashboard = dashboards[0]

    request = {
        "dashboard": {
            "id": None,
            "uid": None,
            "title": "test dashboard_copy_alert",
            "tags": ["alexey"],
            "timezone": "browser",
            "schemaVersion": 16,
            "version": 0,
            "refresh": "25s",
            "panels": dashboard["panels"][:1],
        },
        "folderId": None,
        "folderUid": None,
        "message": "Made changes to xyz",
        "overwrite": True,
    }
    request["dashboard"]["panels"][0]["id"] = 100
    for counter, id_string in enumerate(["-20", "-22"]):
        with open(
            os.path.join(cache_dir, "panel_sample_1.json"), encoding="UTF-8"
        ) as file_handler:
            str_panel = file_handler.read()
            str_panel = grafana_api.replacement_engine.perform_raw_string_replacements(
                str_panel,
                {
                    "STRING_REPLACEMENT_H_ID": id_string,
                    "STRING_REPLACEMENT_PANEL_TITLE": f"panel {id_string} count",
                },
            )
        dict_panel1 = json.loads(str_panel)
        dict_panel1["gridPos"]["x"] = 0
        dict_panel1["gridPos"]["y"] = counter * 8
        dict_panel1["id"] = counter * 2

        request["dashboard"]["panels"].append(dict_panel1)

        with open(
            os.path.join(cache_dir, "panel_sample_2.json"), encoding="UTF-8"
        ) as file_handler:
            str_panel2 = file_handler.read()
            str_panel2 = grafana_api.replacement_engine.perform_raw_string_replacements(
                str_panel2,
                {
                    "STRING_REPLACEMENT_H_ID": id_string,
                    "STRING_REPLACEMENT_PANEL_TITLE": f"panel {id_string} success",
                },
            )
        dict_panel2 = json.loads(str_panel2)
        dict_panel2["gridPos"]["x"] = 12
        dict_panel2["gridPos"]["y"] = counter * 8
        dict_panel2["id"] = counter * 2 + 1
        request["dashboard"]["panels"].append(dict_panel2)
    grafana_api.create_dashboard_raw(request)


@pytest.mark.skip(reason="Can not test")
def test_init_folders_and_dashboards():
    """
    Test folders and dashboards initiation
    @return:
    """
    grafana_api.init_folders_and_dashboards()
    assert isinstance(grafana_api.dashboards, list)
    dashboards = [dashboard.dict_src for dashboard in grafana_api.dashboards]
    with open(dashboards_cache_file, "w", encoding="UTF-8") as file_handler:
        json.dump(dashboards, file_handler, indent=4)


@pytest.mark.skip(reason="Can not test")
def test_init_datasources():
    """
    Datasource initiation.
    @return:
    """
    grafana_api.init_datasources()
    assert isinstance(grafana_api.datasources, list)
    with open(dashboards_datasource_file, "w", encoding="UTF-8") as file_handler:
        json.dump(
            [obj.dict_src for obj in grafana_api.datasources], file_handler, indent=4
        )


@pytest.mark.skip(reason="Can not test")
def test_provision_datasource():
    """
    Provision datasource
    @return:
    """
    dashboard = Dashboard({})
    dashboard.title = "test dashboard1"
    grafana_api.provision_datasource(dashboard)


@pytest.mark.skip(reason="Can not test")
def test_init_rule_namespaces():
    """
    Namespace and rules initiation
    @return:
    """
    grafana_api.init_rule_namespaces()
    with open(rules_cache_file, "w", encoding="UTF-8") as file_handler:
        json.dump(grafana_api.rule_namespaces, file_handler, indent=4)


@pytest.mark.skip(reason="Can not test")
def test_init_folders():
    """
    Dashboard folders initiation
    @return:
    """
    grafana_api.init_folders()


if __name__ == "__main__":
    # test_init_grafana_api()
    # test_provision_dashboard()
    # test_init_folders_and_dashboards()
    # test_provision_datasource()
    # test_create_dashboard_raw()
    # test_create_dashboard_generated_raw()
    # test_init_rule_namespaces()
    # test_init_folders()
    # test_init_datasources()
    test_create_rule_raw()
