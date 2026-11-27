# Horey GitHub UI

FastAPI server presenting GitHub data collected by `horey.github_api`.

| Endpoint        | Description            |
|-----------------|------------------------|
| `/health-check` | `200 ok`               |
| `/dashboard`    | Dashboard (WIP)        |

## Configuration

`fetch_repos` lists all the repositories under the `owner` organization using `horey.github_api`.

The server reads its configuration file (`.json` or `.py`) from the `GITHUB_UI_CONFIGURATION_FILE_PATH` environment variable.
The file sets `github_api_configuration_file_path`, the path of the GithubAPI configuration file:

```json
{"github_api_configuration_file_path": "/path/to/github_api_configuration.json"}
```

The GithubAPI configuration file holds the `pat` and `owner` values:

```json
{"pat": "<github personal access token>", "owner": "<organization>"}
```

```bash
export GITHUB_UI_CONFIGURATION_FILE_PATH=/path/to/github_ui_configuration.json
```

Without it, or with a missing file, `/fetch_repos` answers `503`.

## Run locally

```bash
python -m horey.github_ui.server      # listens on 0.0.0.0:8080
```

## Docker

The required horey packages are resolved from the `requirements.txt` files and installed with `pip_api_make.py`.
Build from the horey repository root:

```bash
docker build -f github_ui/docker/Dockerfile -t horey-github-ui .
```

The container starts with [docker/run.sh](docker/run.sh), which:
1. Reads `github_api_configuration_file_path` and `postgres_api_configuration_file_path` from the baked-in GitHub UI configuration
   ([docker/github_ui_configuration.json](docker/github_ui_configuration.json), copied to
   `/opt/horey/config/github_ui_configuration.json`; `GITHUB_UI_CONFIGURATION_FILE_PATH` points to it).
2. Downloads the secrets `GITHUB_API_CONFIGURATION_SECRET_NAME` and `POSTGRES_API_CONFIGURATION_SECRET_NAME` from AWS Secrets Manager
   to those paths with `horey.infrastructure_api.secrets_api_actor` (`--action get_secret_file`):
   - GitHub API configuration: `{"pat": "<token>", "owner": "<organization>"}`
   - Postgres API configuration: `{"host": "...", "port": 5432, "database": "...", "username": "...", "password": "..."}`

   The files are readable by the container user only and are never part of the image.
3. Starts `horey.github_ui.server`.

```bash
docker run --rm -p 8080:8080 \
    -e GITHUB_API_CONFIGURATION_SECRET_NAME=<secret name> \
    -e GITHUB_API_CONFIGURATION_SECRET_REGION=<region> \
    -e POSTGRES_API_CONFIGURATION_SECRET_NAME=<secret name> \
    -e POSTGRES_API_CONFIGURATION_SECRET_REGION=<region> \
    -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_SESSION_TOKEN \
    horey-github-ui
```

`POSTGRES_API_CONFIGURATION_SECRET_REGION` is optional and defaults to the GitHub secret's region.
AWS credentials must be available in the container (variables as above, or an instance/task role).
If a download fails the container exits without starting the server. `make run` does all of this using the AWS `default` profile.

To bake in another UI configuration file:

```bash
docker build -f github_ui/docker/Dockerfile --build-arg GITHUB_UI_CONFIGURATION_FILE=<path relative to the repo root> -t horey-github-ui .
```
