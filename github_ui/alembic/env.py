"""
Alembic environment.

The database is the one of the Postgres API configuration, which is referenced by the GitHub UI configuration
file in GITHUB_UI_CONFIGURATION_FILE_PATH (the same way the server finds it).
A connection can be passed in config.attributes["connection"] instead, e.g. by tests.
"""

import os
from logging.config import fileConfig

from alembic import context

from horey.github_ui.db_models import Base
from horey.github_ui.github_ui_configuration_policy import GithubUIConfigurationPolicy
from horey.postgres_api.postgres_api import PostgresAPI
from horey.postgres_api.postgres_api_configuration_policy import PostgresAPIConfigurationPolicy

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_engine():
    """
    Engine of the configured Postgres API.

    :return:
    """

    configuration_file_path = os.environ.get("GITHUB_UI_CONFIGURATION_FILE_PATH")
    if not configuration_file_path:
        raise ValueError("GITHUB_UI_CONFIGURATION_FILE_PATH must be set")

    configuration = GithubUIConfigurationPolicy()
    configuration.configuration_file_full_path = configuration_file_path
    configuration.init_from_file()
    if configuration.postgres_api_configuration_file_path is None:
        raise ValueError("postgres_api_configuration_file_path was not set")

    postgres_api_configuration = PostgresAPIConfigurationPolicy()
    postgres_api_configuration.configuration_file_full_path = configuration.postgres_api_configuration_file_path
    postgres_api_configuration.init_from_file()
    return PostgresAPI(configuration=postgres_api_configuration).engine


def run_migrations_online() -> None:
    """
    Run migrations against the database.

    :return:
    """

    connection = config.attributes.get("connection")
    if connection is not None:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
        return

    connectable = get_engine()
    try:
        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)

            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()


if context.is_offline_mode():
    raise NotImplementedError("Offline migrations are not supported: the database URL holds the password")

run_migrations_online()
