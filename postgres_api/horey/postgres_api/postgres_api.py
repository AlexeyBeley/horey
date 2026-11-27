"""
Postgres API.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine

from horey.h_logger import get_logger
from horey.postgres_api.postgres_api_configuration_policy import PostgresAPIConfigurationPolicy

logger = get_logger()


class PostgresAPI:
    """
    Main class.

    """

    DRIVER_NAME = "postgresql+psycopg"

    def __init__(self, configuration: PostgresAPIConfigurationPolicy = None):
        self.configuration = configuration
        self._engine = None

    @property
    def url(self) -> URL:
        """
        Connection URL. Built with URL.create, so special characters in the password are safe.

        :return:
        """

        return URL.create(
            self.DRIVER_NAME,
            username=self.configuration.username,
            password=self.configuration.password,
            host=self.configuration.host,
            port=self.configuration.port,
            database=self.configuration.database,
        )

    @property
    def engine(self) -> Engine:
        """
        Lazy engine.

        :return:
        """

        if self._engine is None:
            self._engine = create_engine(self.url, pool_pre_ping=True)
        return self._engine

    @engine.setter
    def engine(self, value):
        self._engine = value

    def check_connection(self):
        """
        Raise if the database is unreachable.

        :return:
        """

        with self.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True

    def execute(self, statement: str, parameters: dict = None):
        """
        Execute single statement in its own transaction. Returns rows as dicts for statements which return rows.

        :param statement: SQL with :named parameters.
        :param parameters:
        :return:
        """

        with self.engine.begin() as connection:
            result = connection.execute(text(statement), parameters or {})
            if result.returns_rows:
                return [dict(row) for row in result.mappings()]
        return []

    def dispose(self):
        """
        Close all pooled connections.

        :return:
        """

        if self._engine is not None:
            self._engine.dispose()
            self._engine = None
