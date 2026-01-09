"""
Init and cache AWS objects.

"""
import shutil
import sys
from pathlib import Path

import pytest
sys.path.append(str(Path(__file__).parent))
from test_utils import init_from_secrets_api

from horey.aws_api.aws_api import AWSAPI
from horey.common_utils.common_utils import CommonUtils
from horey.configuration_policy.configuration_policy import ConfigurationPolicy
from horey.h_logger import get_logger
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.db_api_configuration_policy import DBAPIConfigurationPolicy
# Uncomment next line to save error lines to /tmp/error.log


# pylint: disable= missing-function-docstring

mock_values_file_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_db_api_mocks.py"
mock_values = CommonUtils.load_module(mock_values_file_path)


logger = get_logger()

aws_api = AWSAPI()

class Configuration(ConfigurationPolicy):
    """
    Tests configuration
    """

    TEST_CONFIG = None

    def __init__(self):
        super().__init__()
        self._db_name = None
        self._environment_api_configuration_file_secret_name = None
        self._glue_s3_bucket_name = None
        self._glue_s3_bucket_path = None

    @property
    def environment_api_configuration_file_secret_name(self):
        return self._environment_api_configuration_file_secret_name

    @environment_api_configuration_file_secret_name.setter
    def environment_api_configuration_file_secret_name(self, value: Path):
        self._environment_api_configuration_file_secret_name = value

    @property
    def db_name(self):
        return self._db_name

    @db_name.setter
    def db_name(self, value: Path):
        self._db_name = value

    @property
    def glue_s3_bucket_name(self):
        return self._glue_s3_bucket_name

    @glue_s3_bucket_name.setter
    def glue_s3_bucket_name(self, value):
        self._glue_s3_bucket_name = value

    @property
    def glue_s3_bucket_path(self):
        return self._glue_s3_bucket_path

    @glue_s3_bucket_path.setter
    def glue_s3_bucket_path(self, value):
        self._glue_s3_bucket_path = value



@pytest.fixture(scope="session", autouse=True)
def setup_test_config():
    Configuration.TEST_CONFIG = init_from_secrets_api(Configuration, mock_values.secret_name)
    yield Configuration.TEST_CONFIG

@pytest.fixture(name="env_api_integration")
def fixture_env_api_integration():
    env_configuration = init_from_secrets_api(EnvironmentAPIConfigurationPolicy, Configuration.TEST_CONFIG.environment_api_configuration_file_secret_name)
    env_configuration.data_directory_path = Path("/tmp/test_data")
    infrastructure_api = InfrastructureAPI()
    environment_api = infrastructure_api.get_environment_api(env_configuration, aws_api=aws_api)
    yield environment_api
    if env_configuration.data_directory_path.exists():
        shutil.rmtree(env_configuration.data_directory_path)


@pytest.fixture(name="db_api")
def fixture_db_api(env_api_integration):
    infrastructure_api = InfrastructureAPI()
    db_api_configuration = DBAPIConfigurationPolicy()
    yield infrastructure_api.get_db_api(db_api_configuration, env_api_integration)

@pytest.mark.unit
def test_provision_glue_database(db_api):
    db_test  = db_api.provision_glue_database("test")
    assert db_test


@pytest.mark.unit
def test_provision_glue_database_tags(db_api):
    db_test  = db_api.provision_glue_database("test")
    db_test.tags = None
    db_api.environment_api.aws_api.glue_client.provision_database(db_test)
    assert db_test.tags == {}
    db_test = db_api.provision_glue_database("test")
    assert db_test.tags is not None


@pytest.mark.unit
def test_provision_glue_table(db_api):
    storage_descriptor = {
            "Columns": [
                {
                    "Name": "column_test",
                    "Type": "int",
                    "Comment": "column_test"
                }
            ],
            "Location": f"s3://{Configuration.TEST_CONFIG.glue_s3_bucket_name}/{Configuration.TEST_CONFIG.glue_s3_bucket_path}",
            "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
            "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
            "Compressed": False,
            "NumberOfBuckets": -1,
            "SerdeInfo": {
                "SerializationLibrary": "org.openx.data.jsonserde.JsonSerDe",
                "Parameters": {
                    "serialization.format": "1"
                }
            },
            "BucketColumns": [],
            "SortColumns": [],
            "Parameters": {},
            "SkewedInfo": {
                "SkewedColumnNames": [],
                "SkewedColumnValues": [],
                "SkewedColumnValueLocationMaps": {}
            },
            "StoredAsSubDirectories": False
        }
    partition_keys = [
        {
            "Name": "partition_key_test",
            "Type": "string"
        }
    ]
    ret = db_api.provision_glue_table("test", "test", storage_descriptor, partition_keys)
    assert ret


@pytest.mark.unit
def test_dispose_glue_table(db_api):
    ret = db_api.dispose_glue_table("test", "test")
    assert ret



@pytest.mark.unit
def test_dispose_glue_database(db_api):
    ret = db_api.dispose_glue_database("test")
    assert ret
