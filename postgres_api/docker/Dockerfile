# Local PostgreSQL for horey.postgres_api development.
# Pinned to 17: from 18 the image keeps data in a version specific subdirectory,
# which changes where the volume has to be mounted.
FROM postgres:17-bookworm

ENV POSTGRES_USER=postgres
ENV POSTGRES_DB=postgres
# POSTGRES_PASSWORD is intentionally not set here, pass it with `docker run -e`.

# Data lives in a subdirectory of the mounted volume: initdb refuses a mount point
# which is not empty (e.g. lost+found).
ENV PGDATA=/var/lib/postgresql/data/pgdata

EXPOSE 5432
