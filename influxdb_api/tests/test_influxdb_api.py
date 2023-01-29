"""
Influxdb tools tests

"""
import os
from horey.influxdb_api.influxdb_api import InfluxDBAPI
from horey.influxdb_api.influxdb_api_configuration_policy import InfluxDBAPIConfigurationPolicy
from horey.common_utils.common_utils import CommonUtils

influxdb_ignore_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "influxdb")
configuration = InfluxDBAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.join(influxdb_ignore_dir, "influxdb_api_config.py")
configuration.init_from_file()
influxdb_api = InfluxDBAPI(configuration)

mock_values_file_path = os.path.abspath(
    os.path.join(influxdb_ignore_dir, "mock_values.py"
    )
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


def test_parse_journalctl():
    """
    Parse get/post request.

    :return:
    """

    influxdb_api.parse_journalctl("/influx/journalctl.txt")


def test_init_measurements():
    """
    Parse get/post request.

    :return:
    """

    influxdb_api.init_measurements(mock_values["db_name"])


def test_yield_series():
    """
    Parse get/post request.

    :return:
    """

    for measurement_series in influxdb_api.yield_series(mock_values["db_name"], mock_values["measurement"]):
        index_tmp = 42
        breakpoint()
        for lst_value in measurement_series["values"]:
            if type(lst_value[index_tmp]) != int and lst_value[index_tmp] is not None:
                breakpoint()


def test_write():
    influxdb_api.write(mock_values["db_name"], mock_values["measurement"], mock_values["columns"], mock_values["values"])


if __name__ == "__main__":
    #test_parse_journalctl()
    #test_init_measurements()
    #test_yield_series()
    test_write()
