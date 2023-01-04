"""
Influxdb tools tests

"""
from horey.influxdb_api.influxdb_api import InfluxDBAPI

influxdb_api = InfluxDBAPI(configuration=None)


def test_parse_journalctl():
    """
    Parse get/post request.

    :return:
    """

    influxdb_api.parse_journalctl("/influx/journalctl.txt")

# endregion


if __name__ == "__main__":

    test_parse_journalctl()
