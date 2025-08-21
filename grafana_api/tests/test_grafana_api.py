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
from horey.grafana_api.panel import Panel

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


# pylint: disable= missing-function-docstring
@pytest.fixture(name="grafana_api")
def fixture_grafana_api():
    """
    Test Grafana API initiation
    @return:
    """
    _grafana_api = GrafanaAPI(configuration=configuration)
    yield _grafana_api


@pytest.mark.done
def test_init_grafana_api():
    """
    Test Grafana API initiation
    @return:
    """
    _grafana_api = GrafanaAPI(configuration=configuration)
    assert isinstance(_grafana_api, GrafanaAPI)


@pytest.mark.skip(reason="Can not test")
def test_provision_dashboard(grafana_api):
    """
    Test dashboard object provisioning
    @return:
    """
    dashboard = Dashboard({})
    dashboard.title = "test dashboard1"
    grafana_api.provision_dashboard(dashboard)


def generate_line_panel(file_name):
    panel = Panel({
        "collapsed": False,
        "gridPos": {
            "h": 1,
            "w": 24,
            "x": None,
            "y": None
        },
        "id": None,
        "title": f"{file_name} monitoring graphs",
        "type": "row"
    })
    return panel


self_path = os.path.dirname(os.path.abspath(__file__))


def generate_influx_monitoring_panel(measurement_name, panel_name):
    with open(os.path.join(self_path, "test_panel", "panel_1.json"), encoding="utf-8") as fh:
        dict_src = json.load(fh)
    # with open(os.path.join(self_path, "test_panel", "panel_count_interval.json")) as fh:
    #    dict_src = json.load(fh)

    panel = Panel(dict_src)
    panel.title = panel_name

    panel.targets[0]["measurement"] = measurement_name
    panel.targets[0]["select"][0][0]["params"][0] = panel_name

    return panel


@pytest.mark.skip(reason="Can not test")
def test_create_influxdb_monitor_dashboard(grafana_api):
    """
    mkdir ./telegraf_structure
    influx -database telegraf -execute 'show measurements' >> ./telegraf_structure/measurements
    influx -database telegraf -execute 'show field keys from influxdb_httpd' >> ./telegraf_structure/influxdb_httpd
    """

    dashboard = Dashboard({})
    dashboard.id = "1111"
    dashboard.title = "InfluxDB Monitoring"
    dashboard.tags = ["monitoring"]

    with open("./telegraf_structure/measurements", encoding="utf-8") as fh:
        lines = [line.strip() for line in fh.readlines()]
        lines = lines[3:]
    for measurement in lines:
        print(
            f"influx -database telegraf -execute 'show field keys from {measurement}' >> ./telegraf_structure/{measurement}")

    for file_name in os.listdir("./telegraf_structure"):
        if file_name == "measurements":
            continue

        panel = generate_line_panel(file_name)
        dashboard.add_panel(panel)

        with open(os.path.join("./telegraf_structure", file_name), encoding="utf-8") as fh:
            lines = [line.strip() for line in fh.readlines()]
            lines = lines[3:]
        for line in lines:
            panel = generate_influx_monitoring_panel(file_name, line.split()[0])
            dashboard.add_panel(panel)
    grafana_api.provision_dashboard(dashboard)


@pytest.mark.unit
def test_create_dashboard_raw(grafana_api):
    """
    Test dashboard creation from raw dict
    @return:
    """

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
            "panels": [
                {
                    "title": "Random Walk Data",
                    "type": "graph",
                    "gridPos": {"x": 0, "y": 0, "w": 12, "h": 9},
                    "targets": [
                        {
                            "datasource": {"type": "testdata"},
                            "scenarioId": "random_walk"
                        }
                    ],
                    "options": {}
                }
            ],
        },
        "folderId": None,
        "folderUid": None,
        "message": "Made changes to xyz",
        "overwrite": True,
    }
    grafana_api.create_dashboard_raw(request)


@pytest.mark.skip(reason="Can not test")
def test_create_rule_raw(grafana_api):
    request = {}
    # with open(os.path.join(cache_dir, "dashboards.json"), encoding="utf-8") as file_handler:
    #    pass

    namespace = "critical_alerts"
    grafana_api.create_rule_raw(request, namespace)


@pytest.mark.skip(reason="Can not test")
def test_create_dashboard_generated_raw(grafana_api):
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


@pytest.mark.done
def test_init_folders_and_dashboards(grafana_api):
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
def test_init_datasources(grafana_api):
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
def test_provision_datasource(grafana_api):
    """
    Provision datasource
    @return:
    """
    dashboard = Dashboard({})
    dashboard.title = "test dashboard1"
    grafana_api.provision_datasource(dashboard)


@pytest.mark.skip(reason="Can not test")
def test_init_rule_namespaces(grafana_api):
    """
    Namespace and rules initiation
    @return:
    """
    grafana_api.init_rule_namespaces()
    with open(rules_cache_file, "w", encoding="UTF-8") as file_handler:
        json.dump(grafana_api.rule_namespaces, file_handler, indent=4)


@pytest.mark.skip(reason="Can not test")
def test_init_folders(grafana_api):
    """
    Dashboard folders initiation
    @return:
    """
    grafana_api.init_folders()


@pytest.mark.skip(reason="Can not test")
def test_generate_token(grafana_api):
    """
    Dashboard folders initiation
    @return:
    """
    pass


@pytest.mark.unit
def test_provision_dashboard(grafana_api):
    """
    Test dashboard creation from raw dict
    @return:
    """

    dict_src = {
  "metadata": {
    "name": "gdxccn",
    "annotations": {
      "grafana.app/folder": "bev54vrop8dmob"
    },
  },
  "spec": {
    "annotations": {
    "list": [
      {
        "datasource": {
          "type": "datasource",
          "uid": "grafana"
        },
        "enable": True,
        "hide": False,
        "iconColor": "red",
        "name": "Example annotation",
        "target": {
          "limit": 100,
          "matchAny": False,
          "tags": [],
          "type": "dashboard"
        }
      }]
    },
    "editable": True,
    "fiscalYearStartMonth": 0,
    "graphTooltip": 0,
    "links": [
      {
        "asDropdown": False,
        "icon": "external link",
        "includeVars": False,
        "keepTime": False,
        "tags": [],
        "targetBlank": False,
        "title": "Example Link",
        "tooltip": "",
        "type": "dashboards",
        "url": ""
      }
    ],
    "panels": [
      {
        "datasource": {
          "type": "datasource",
          "uid": "grafana"
        },
        "description": "With a description",
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "palette-classic"
            },
            "custom": {
              "axisBorderShow": False,
              "axisCenteredZero": False,
              "axisColorMode": "text",
              "axisLabel": "",
              "axisPlacement": "auto",
              "barAlignment": 0,
              "barWidthFactor": 0.6,
              "drawStyle": "line",
              "fillOpacity": 0,
              "gradientMode": "none",
              "hideFrom": {
                "legend": False,
                "tooltip": False,
                "viz": False
              },
              "insertNulls": False,
              "lineInterpolation": "linear",
              "lineWidth": 1,
              "pointSize": 5,
              "scaleDistribution": {
                "type": "linear"
              },
              "showPoints": "auto",
              "spanNulls": False,
              "stacking": {
                "group": "A",
                "mode": "none"
              },
              "thresholdsStyle": {
                "mode": "off"
              }
            },
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green"
                },
                {
                  "color": "red",
                  "value": 80
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 0
        },
        "id": 1,
        "options": {
          "legend": {
            "calcs": [],
            "displayMode": "list",
            "placement": "bottom",
            "showLegend": True
          },
          "tooltip": {
            "hideZeros": False,
            "mode": "single",
            "sort": "none"
          }
        },
        "pluginVersion": "12.0.0",
        "targets": [
          {
            "datasource": {
              "type": "datasource",
              "uid": "grafana"
            },
            "refId": "A"
          }
        ],
        "title": "Example panel",
        "type": "timeseries"
      }
    ],
    "preload": False,
    "schemaVersion": 41,
    "tags": ["example"],
    "templating": {
      "list": [
        {
          "current": {
            "text": "",
            "value": ""
          },
          "definition": "",
          "description": "example description",
          "label": "ExampleLabel",
          "name": "ExampleVariable",
          "options": [],
          "query": "",
          "refresh": 1,
          "regex": "cluster",
          "type": "query"
        }
      ]
    },
    "time": {
      "from": "now-6h",
      "to": "now"
    },
    "timepicker": {},
    "timezone": "browser",
    "title": "Example Dashboard",
    "version": 0
  }
}
    dashboard = Dashboard(dict_src)
    grafana_api.provision_dashboard(dashboard)


@pytest.mark.unit
def test_init_dashboards(grafana_api):
    """
    Dashboard folders initiation

    @return:
    """

    assert grafana_api.init_dashboards()


@pytest.mark.unit
def test_init_folders(grafana_api):
    """
    Dashboard folders initiation

    @return:
    """

    assert grafana_api.init_folders()