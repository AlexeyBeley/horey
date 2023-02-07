"""
Influxdb tools tests

"""
import os

from horey.influxdb_api.kapacitor_api import KapacitorAPI
from horey.influxdb_api.kapacitor_api_configuration_policy import KapacitorAPIConfigurationPolicy
from horey.influxdb_api.kapacitor_api import Task
from horey.common_utils.common_utils import CommonUtils


kapacitor_ignore_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore", "kapacitor")

mock_values_file_path = os.path.abspath(
    os.path.join(
        kapacitor_ignore_dir, "mock_values.py"
    )
)

mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

configuration = KapacitorAPIConfigurationPolicy()
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


def test_provision_from_cache():
    kapacitor_api.provision_from_cache(os.path.join(kapacitor_ignore_dir, "tasks.json"))


def test_provision_task():
    dict_src = {
            "id": "test-id",
            "type": "stream",
            "dbrps": [
      {
        "db": "tests",
        "rp": "autogen"
      }
    ],
            "script": mock_values["provision_alert_script"],
            "status": "enabled"
        }
    task = Task(dict_src)

    kapacitor_api.provision_task(task)


def test_disable_all_tasks():
    kapacitor_api.disable_all_tasks()


def test_enable_all_tasks():
    kapacitor_api.enable_all_tasks()


if __name__ == "__main__":
    # test_init_tasks()
    # test_provision_task()
    test_disable_all_tasks()
    # test_enable_all_tasks()
    #test_cache_tasks()
    #test_provision_from_cache()
