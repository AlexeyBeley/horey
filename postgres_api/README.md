# Horey Postgres API

Thin PostgreSQL client built on SQLAlchemy 2.x and psycopg 3.

```python
from horey.postgres_api.postgres_api import PostgresAPI
from horey.postgres_api.postgres_api_configuration_policy import PostgresAPIConfigurationPolicy

config = PostgresAPIConfigurationPolicy()
config.host = "localhost"
config.port = 5432
config.database = "postgres"
config.username = "postgres"
config.password = "secret"

postgres_api = PostgresAPI(config)
postgres_api.check_connection()
rows = postgres_api.execute("SELECT id FROM items WHERE name = :name", {"name": "a"})
```
