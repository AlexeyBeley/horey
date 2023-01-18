"""
Influxdb tools tests

"""
import os

from horey.influxdb_api.kapacitor_api import KapacitorAPI
from horey.influxdb_api.kapacitor_api_configuration_policy import KapacitorAPIConfigurationPolicy

configuration = KapacitorAPIConfigurationPolicy()
kapacitor_ignore_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "kapacitor")
configuration.configuration_file_full_path = os.path.join(kapacitor_ignore_dir, "kapacitor_api_config.py")
configuration.init_from_file()
kapacitor_api = KapacitorAPI(configuration)

# pylint: disable=missing-function-docstring


def test_init_tasks():
    """
    Parse get/post request.

    :return:
    """

    kapacitor_api.init_tasks()


def test_cache_tasks():
    kapacitor_api.cache_tasks(os.path.join(kapacitor_ignore_dir, "tasks.json"))


if __name__ == "__main__":
    # test_init_tasks()
    test_cache_tasks()
