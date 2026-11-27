"""
Testing postgres api
"""
from pathlib import Path

import pytest
from horey.postgres_api.postgres_api import PostgresAPI
from horey.postgres_api.postgres_api_configuration_policy import PostgresAPIConfigurationPolicy

config = PostgresAPIConfigurationPolicy()
config.configuration_file_full_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_postgres_api_configuration.py"
config.init_from_file()


# pylint: disable= missing-function-docstring


@pytest.mark.wip
def test_check_connection():
    postgres_api = PostgresAPI(config)
    assert postgres_api.check_connection()


@pytest.mark.wip
def test_execute():
    postgres_api = PostgresAPI(config)
    assert postgres_api.execute("SELECT 1 AS one") == [{"one": 1}]
