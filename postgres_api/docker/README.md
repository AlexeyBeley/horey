# Local PostgreSQL

Runs PostgreSQL 17 in Docker. Data is stored on the host in `/opt/horey/postgres`,
so it survives container removal.

## Build

```bash
cd postgres_api/docker
docker build -t horey-postgres .
```

## Prepare the data directory

```bash
sudo mkdir -p /opt/horey/postgres
```

The directory must be writable by the container.

* Linux: the container's `postgres` user (uid 999) writes there.
  ```bash
  sudo chown 999:999 /opt/horey/postgres
  ```
* macOS (Docker Desktop): container users are mapped to your Mac user, so the directory
  must be owned by you, and `/opt/horey` must be listed under Settings -> Resources -> File sharing.
  ```bash
  sudo chown -R "$(whoami)" /opt/horey/postgres
  ```

## Run

```bash
docker run -d --name horey-postgres \
    -e POSTGRES_PASSWORD=change_me \
    -p 5432:5432 \
    -v /opt/horey/postgres:/var/lib/postgresql/data \
    --network pgnet \
    horey-postgres
```

`POSTGRES_PASSWORD` is only used the first time, when the data directory is empty.
Publish as `-p 127.0.0.1:5432:5432` to keep the database reachable from this machine only.

## Check

```bash
docker logs horey-postgres
docker exec -it horey-postgres psql -U postgres -c "SELECT version();"
```

Connection settings for `PostgresAPIConfigurationPolicy`:

| Setting  | Value       |
|----------|-------------|
| host     | `localhost` |
| port     | `5432`      |
| database | `postgres`  |
| username | `postgres`  |
| password | the one you passed in `POSTGRES_PASSWORD` |

## Troubleshooting

`mounts denied: The path /opt/horey/postgres is not shared from the host`
(Docker Desktop on macOS): add `/opt/horey` under Docker Desktop -> Settings -> Resources ->
File sharing, click "Apply & restart", then run the command again. Make sure the directory
exists first (`sudo mkdir -p /opt/horey/postgres`).

`mkdir: cannot create directory '/var/lib/postgresql/data/pgdata': Permission denied`:
the data directory is not writable by the container, see "Prepare the data directory" above.
Fix the ownership, then `docker rm -f horey-postgres` and run again.

If you don't need the data at a specific host path, use a named volume instead, no sharing needed:
`-v horey_postgres:/var/lib/postgresql/data`.

## Stop / start / remove

```bash
docker stop horey-postgres
docker start horey-postgres
docker rm -f horey-postgres      # data stays in /opt/horey/postgres
```

## Reset the database

```bash
docker rm -f horey-postgres
sudo rm -rf /opt/horey/postgres/pgdata
```
