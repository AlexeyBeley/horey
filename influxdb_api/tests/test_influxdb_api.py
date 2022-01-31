import pdb

import pytest
import os

from horey.influxdb_api.influxdb_api import InfluxDBAPI
from horey.influxdb_api.influxdb_api_configuration_policy import InfluxDBAPIConfigurationPolicy


configuration = InfluxDBAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                 "influxdb_api_configuration_values.py"))
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
    assert len(influxdb_api.rules) > 0
# endregion


if __name__ == "__main__":
    #test_init_sources()
    #test_init_kapacitors()
    test_init_rules()
