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

# pylint: disable= missing-function-docstring


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
        for lst_value in measurement_series["values"]:
            if not isinstance(lst_value[index_tmp], int) and lst_value[index_tmp] is not None:
                raise Exception("not int")


def test_cast_measurement():
    """
    Parse get/post request.

    :return:
    """
    influxdb_api.cast_measurement(mock_values["db_name"]+"_tmp", mock_values["db_name"], mock_values["measurement"])


def test_write():
    influxdb_api.write(mock_values["db_name"], mock_values["measurement"], mock_values["columns"], mock_values["values"])


def test_count_measurement():
    influxdb_api.count_measurement(mock_values["db_name"], mock_values["measurement"])


def test_find_max_count():
    ret = influxdb_api.find_max_count(mock_values["db_name"], mock_values["measurement"])
    print(ret)


if __name__ == "__main__":
    #test_parse_journalctl()
    #test_init_measurements()
    #test_yield_series()
    #test_write()
    #test_count_measurement()
    #test_find_max_count()
    #breakpoint()
    test_cast_measurement()
