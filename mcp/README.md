# Horey MCP

MCP server (streamable HTTP) exposing the tools of the installed horey packages to Claude Code
or any other MCP client.

The server has no tools of its own, except `mcp_list_packages`. On start it scans the installed `horey.*`
packages and loads the tools of every package having a `horey/<package_name>/mcp_tools.py` module.

A package can serve several configurations (environments) at once, e.g. dev, staging and production Jenkins
servers, or AWS environments in different regions. See [Multiple configurations](#multiple-configurations).

## Exposing tools from a horey package

Add `horey/<package_name>/mcp_tools.py` to the package, e.g. [jenkins_api](../jenkins_api/horey/jenkins_api/mcp_tools.py):

```python
"""
MCP tools of horey.jenkins_api
"""

from typing import TYPE_CHECKING, Any

from horey.jenkins_api.jenkins_api import JenkinsAPI
from horey.jenkins_api.jenkins_api_configuration_policy import JenkinsAPIConfigurationPolicy

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    :param registry: passed in by horey.mcp
    """

    @registry.cached_per_configuration
    def jenkins_api(configuration_name: str | None) -> JenkinsAPI:
        return JenkinsAPI(registry.get_configuration(JenkinsAPIConfigurationPolicy, configuration_name))

    @registry.tool(read_only=True)
    def get_build(job_name: str, build_number: int, configuration_name: str | None = None) -> dict[str, Any]:
        """Get a Jenkins build: result (None while building), building, duration, url."""
        info = jenkins_api(configuration_name).server.get_build_info(job_name, build_number)
        return {"result": info["result"], "building": info["building"]}

    @registry.tool()
    def trigger_job(job_name: str, parameters: dict[str, str] | None = None,
                    configuration_name: str | None = None) -> int:
        """Trigger a Jenkins job. Returns the queue item id."""
        return jenkins_api(configuration_name).server.build_job(job_name, parameters or {})
```

Rules:

* The tool name is `<package_name>_<function name>`, e.g. `jenkins_api_get_build`.
* Every tool using the configuration takes `configuration_name: str | None = None` as its last parameter and passes
  it to the API factory. The registry then adds `<package_name>_list_configurations` and appends a
  `configuration_name` note to the tool description.
* The docstring is the tool description and the type hints are the input schema. Claude sees only these.
* `read_only=True` for tools which do not change anything. `destructive=True` for tools which delete,
  overwrite or run commands.
* The package does not import `horey.mcp` at run time (only under `TYPE_CHECKING`, for the type hint).
  `mcp_tools.py` is imported only by the MCP server, so it adds no dependencies to the package.
* Create the API object lazily (`@registry.cached_per_configuration`, one object per configuration):
  the configuration is read on the first tool call, a missing configuration fails that call, not the server start.
* Sync tools run in a worker thread, they do not block the server. Still, return fast:
  trigger and return an id, let Claude poll a status tool. Don't wait for builds inside a tool.
* Return small results: a few fields, the last N log lines. Not raw API responses.
* Exceptions are returned to Claude as the tool error text (`<ExceptionType>: <message>`):
  the MCP SDK hides the text of other exceptions, the registry re-raises them as `ToolError`.
* A package failing to load is logged and skipped, the others are served.

A package with many tools can use a `horey/<package_name>/mcp_tools/` package instead: its `__init__.py`
defines `register_mcp_tools(registry)`, e.g. [infrastructure_api](../infrastructure_api/horey/infrastructure_api/mcp_tools/__init__.py)
registers one tools class per API class (`EC2APIMCPTools`, `CloudwatchAPIMCPTools`, ...), imported statically.

Registry helpers:

| Helper | Use |
|--------|-----|
| `registry.get_configuration(PolicyClass, configuration_name=None)` | The package configuration policy, initialized from the configuration file. Default: the only one |
| `@registry.cached_per_configuration` | Decorator for the API factory: one API object per configuration. The factory gets the resolved file name, `None` if the package has no configurations |
| `registry.list_configurations()` | The package configuration file names |
| `registry.resolve_configuration_name(configuration_name)` | The name if it exists, the only one if `None`. Raises when it is unknown, or `None` while there are several |
| `registry.get_configuration_file_path(file_name=None)` | Path of another file (e.g. an SSH key) in the configurations directory, a file name, not a path. Default: the only package configuration |
| `registry.to_jsonable(obj)` | horey objects to JSON: `dict_src` if the object has it, otherwise the public attributes |

## Packages exposing tools

`github_api`, `jenkins_api`, `infrastructure_api`, `provision_constructor`, `azure_api`, `chronograf_api`, `deployer`,
`docker_api`, `git_api`, `grafana_api`, `influxdb_api`, `kubernetes_api`, `opensearch_api`, `pip_api`, `postgres_api`,
`redis_api`, `replacement_engine`, `selenium_api`, `slack_api`, `zabbix_api`, `snyk_api`, `azure_devops_api`.
Call `mcp_list_packages` for the loaded packages and their tools.

What some of them need where the server runs:

| Package | Needs |
|---------|-------|
| `infrastructure_api` | AWS credentials in the container environment (`-e AWS_ACCESS_KEY_ID ...` or a role), `region` and `vpc_name` in its configuration. Secrets are read in `secrets_manager_region` (default: `region`): `infrastructure_api_get_secret` returns the value into the conversation, `infrastructure_api_download_secret_file` writes it to a 0600 file on the server host (in the container when run in docker) and does not return it. CloudWatch Logs: list log groups and streams, filter events by pattern and time range, tail a stream, run Logs Insights queries. Times are durations (`15m`, `2h`, `7d`) or ISO 8601. EC2 (`ec2_*`, in the environment VPC): list/get instances and security groups, start/stop/terminate instances, create security groups, rules, SSH keys and Ubuntu 24.04 instances |
| `docker_api` | The Docker socket: `-v /var/run/docker.sock:/var/run/docker.sock`. No configuration file |
| `deployer`, `provision_constructor` | SSH private keys as files in the configurations directory, passed by file name. `provision_constructor` also needs `deployer` in `HOREY_MCP_PACKAGES` |
| `git_api` | Works on the single repository of its configuration, cloned inside the container |
| `selenium_api` | Chrome, which the image does not include |
| `pip_api` | Nothing: without a configuration it lists the server's own packages |
| `azure_devops_api` | `server_address`, `org_name`, `project_name`, `team_name`, `user` and `password` - a personal access token with the Work Items (Read) scope. The tools are read-only: search (filters or WIQL), read a work item with its description, links and comments, list the iterations |

Tools which change data or run commands are marked destructive, e.g. `postgres_api_execute`, `redis_api_consume_stream`,
`git_api_checkout_remote`, `deployer_run_remote_command`. Claude Code asks before each call unless you allow them.

## Configuration

`MCPServerConfigurationPolicy`, from `--configuration_file_path` and/or `HOREY_MCP_*` environment variables:

| Attribute                 | Environment variable                | Default                          |
|---------------------------|-------------------------------------|----------------------------------|
| `host`                    | `HOREY_MCP_HOST`                    | `127.0.0.1` (`0.0.0.0` in docker) |
| `port`                    | `HOREY_MCP_PORT`                    | `8080`                           |
| `streamable_http_path`    | `HOREY_MCP_STREAMABLE_HTTP_PATH`    | `/mcp`                           |
| `configurations_dir_path` | `HOREY_MCP_CONFIGURATIONS_DIR_PATH` | `/opt/horey/mcp/configurations`  |
| `packages`                | `HOREY_MCP_PACKAGES`                | all, e.g. `jenkins_api,github_api` |
| `allowed_hosts`           | `HOREY_MCP_ALLOWED_HOSTS`           | `127.0.0.1:*,localhost:*,[::1]:*` |

Package configurations are files in `configurations_dir_path` named `<package_name>_configuration.py`
or `<package_name>_configuration.json`, e.g. `jenkins_api_configuration.py`.

## Multiple configurations

A package can have several configuration files: `<package_name>_configuration[_<suffix>].py|json`.
Put everything needed to tell the environments apart into the suffix, Claude chooses by the file name:

```
/opt/horey/mcp/configurations/
    jenkins_api_configuration_dev_horey.py
    jenkins_api_configuration_staging_horey.py
    jenkins_api_configuration_production_horey.json
    infrastructure_api_configuration_dev_horey_us_east_1.py
    infrastructure_api_configuration_production_horey_eu_west_1.py
```

* `<package_name>_list_configurations` returns the file names. The directory is read on each call,
  files added later are served without a restart.
* The tools take `configuration_name`, one of these file names.
* A single configuration is used when `configuration_name` is not passed, so single setups work as before.
* With several configurations, a call without `configuration_name` fails with the list of the names.
  The server never picks one by itself, and its instructions tell Claude to ask the user when the environment
  is not clear.
* Each configuration gets its own API object. `infrastructure_api` creates an `AWSAccount` per configuration,
  with the configuration region, so environments in different regions are served by the same server.

## Run in docker

```bash
cd mcp
make run HOREY_MCP_PACKAGES="jenkins_api github_api"
make claude_add
```

* Only the packages in `HOREY_MCP_PACKAGES` (and their dependencies) are installed in the image.
* `/opt/horey/mcp/configurations` on the host is mounted read-only into the container.
* The server is published on `127.0.0.1:8090` only, it has no authentication.
  Anything able to reach the port can call every tool with the configured credentials.

`make claude_add` runs:

```bash
claude mcp add --scope user --transport http horey http://localhost:8090/mcp
```

Check with `claude mcp list`, or `/mcp` inside Claude Code.

## Run without docker

```bash
cd mcp
make run_local HOREY_MCP_PACKAGES="jenkins_api"
```
