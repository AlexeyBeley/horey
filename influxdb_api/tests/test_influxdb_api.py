import pdb

import pytest
import os

from horey.influxdb_api.influxdb_api import InfluxDBAPI
from horey.influxdb_api.influxdb_api_configuration_policy import (
    InfluxDBAPIConfigurationPolicy,
)
from horey.influxdb_api.dashboard import Dashboard

configuration = InfluxDBAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "..",
        "ignore",
        "influxdb_api_configuration_values.py",
    )
)
configuration.init_from_file()

influxdb_api = InfluxDBAPI(configuration=configuration)


@pytest.mark.skip(reason="Can not test")
def test_init_sources():
    influxdb_api.init_sources()
    assert len(influxdb_api.sources) > 0


@pytest.mark.skip(reason="Can not test")
def test_init_kapacitors():
    influxdb_api.init_kapacitors()
    assert len(influxdb_api.kapacitors) > 0


@pytest.mark.skip(reason="Can not test")
def test_init_rules():
    influxdb_api.init_rules()
    pdb.set_trace()
    assert len(influxdb_api.rules) > 0


@pytest.mark.skip(reason="Can not test")
def test_create_dashboard():
    dashboard = Dashboard(
        {
            "cells": [
                {
                    "x": 5,
                    "y": 5,
                    "w": 4,
                    "h": 4,
                    "name": "usage_user",
                    "queries": [],
                    "type": "line",
                },
                {
                    "x": 0,
                    "y": 0,
                    "w": 4,
                    "h": 4,
                    "name": "usage_system",
                    "queries": [],
                    "type": "line",
                },
            ],
            "name": "lalalalala",
        }
    )
    influxdb_api.provision_dashboard(dashboard)
    assert len(influxdb_api.rules) > 0


# endregion


if __name__ == "__main__":
    # test_init_sources()
    # test_init_kapacitors()
    test_init_rules()
    # test_create_dashboard()
