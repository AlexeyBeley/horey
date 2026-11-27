"""
Testing grafana API
"""
import os
import json
import pytest

from horey.grafana_api.panel import Panel
from horey.grafana_api.grafana_api_configuration_policy import (
    GrafanaAPIConfigurationPolicy,
)


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

self_path = os.path.dirname(os.path.abspath(__file__))

# pylint: disable= missing-function-docstring


@pytest.mark.skip(reason="Can not test")
def test_init_panel():
    with open(os.path.join(self_path, "test_panel", "panel_1.json"), encoding="utf-8") as fh:
        dict_src = json.load(fh)
    panel = Panel(dict_src)
    assert panel.dict_src is not None


@pytest.mark.skip(reason="Can not test")
def test_init_row():
    with open(os.path.join(self_path, "test_panel", "row_1.json"), encoding="utf-8") as fh:
        dict_src = json.load(fh)
    panel = Panel(dict_src)
    assert panel.dict_src is not None


@pytest.mark.skip(reason="Can not test")
def test_generate_request_panel():
    with open(os.path.join(self_path, "test_panel", "panel_1.json"), encoding="utf-8") as fh:
        dict_src = json.load(fh)
    panel = Panel(dict_src)
    ret = panel.generate_create_request()
    print(ret)


@pytest.mark.skip(reason="Can not test")
def test_generate_request_row():
    with open(os.path.join(self_path, "test_panel", "row_1.json"), encoding="utf-8") as fh:
        dict_src = json.load(fh)
    panel = Panel(dict_src)
    ret = panel.generate_create_request()
    print(ret)


if __name__ == "__main__":
    test_init_panel()
    test_init_row()
    test_generate_request_panel()
    test_generate_request_row()
