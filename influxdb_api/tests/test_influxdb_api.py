"""
Influxdb tools tests

"""
import os
import pytest
from horey.influxdb_api.influxdb_api import InfluxDBAPI
from horey.influxdb_api.influxdb_api_configuration_policy import InfluxDBAPIConfigurationPolicy
from horey.common_utils.common_utils import CommonUtils
from horey.h_logger import get_logger

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

logger = get_logger()

# pylint: disable= missing-function-docstring


@pytest.mark.skip
def test_parse_journalctl():
    """
    Parse get/post request.

    :return:
    """

    influxdb_api.parse_journalctl("/influx/journalctl.txt")


@pytest.mark.skip
def test_init_measurements():
    """
    Parse get/post request.

    :return:
    """

    ret = influxdb_api.init_measurements(mock_values["db_name"])
    assert len(ret) > 0


@pytest.mark.skip
def test_yield_series():
    """
    Parse get/post request.

    :return:
    """

    for measurement_series in influxdb_api.yield_series(mock_values["db_name"], mock_values["measurement"]):
        index_tmp = 42
        for lst_value in measurement_series["values"]:
            if not isinstance(lst_value[index_tmp], int) and lst_value[index_tmp] is not None:
                raise ValueError("not int")


@pytest.mark.unit
def test_cast_measurement():
    """
    Parse get/post request.

    :return:
    """
    influxdb_api.cast_measurement(mock_values["backup_db_name"], mock_values["db_name"], mock_values["measurement"])


@pytest.mark.skip
def test_write():
    influxdb_api.write(mock_values["db_name"], mock_values["measurement"], mock_values["columns"],
                       mock_values["values"])


@pytest.mark.unit
def test_count_measurement():
    ret = influxdb_api.count_measurement(mock_values["db_name"], mock_values["measurement"])
    logger.info(f'Measurements count {mock_values["db_name"]}, {mock_values["measurement"]}, {len(ret)}')
    assert len(ret)


@pytest.mark.skip
def test_find_max_count():
    ret = influxdb_api.find_max_count(mock_values["db_name"], mock_values["measurement"])
    print(ret)
