"""
Testing chronograf api
"""
import os
import pytest

from horey.chronograf_api.chronograf_api import ChronografAPI
from horey.chronograf_api.chronograf_api_configuration_policy import (
    ChronografAPIConfigurationPolicy,
)
from horey.chronograf_api.dashboard import Dashboard

configuration = ChronografAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "..",
        "ignore",
        "chronograf_api_configuration_values.py",
    )
)
configuration.init_from_file()

chronograf_api = ChronografAPI(configuration=configuration)

# pylint: disable= missing-function-docstring


@pytest.mark.skip(reason="Can not test")
def test_init_sources():
    chronograf_api.init_sources()
    assert len(chronograf_api.sources) > 0


@pytest.mark.skip(reason="Can not test")
def test_init_kapacitors():
    chronograf_api.init_kapacitors()
    assert len(chronograf_api.kapacitors) > 0


@pytest.mark.skip(reason="Can not test")
def test_init_rules():
    chronograf_api.init_rules()
    assert len(chronograf_api.rules) > 0


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
    chronograf_api.provision_dashboard(dashboard)
    assert len(chronograf_api.rules) > 0


# endregion


if __name__ == "__main__":
    # test_init_sources()
    # test_init_kapacitors()
    test_init_rules()
    # test_create_dashboard()
