# Horey MCP

MCP server (streamable HTTP) exposing the tools of the installed horey packages to Claude Code
or any other MCP client.

The server has no tools of its own, except `mcp_list_packages`. On start it scans the installed `horey.*`
packages and loads the tools of every package having a `horey/<package_name>/mcp_tools.py` module.

## Exposing tools from a horey package

Add `horey/<package_name>/mcp_tools.py` to the package, e.g. [jenkins_api](../jenkins_api/horey/jenkins_api/mcp_tools.py):

```python
"""
MCP tools of horey.jenkins_api
"""

import functools
from typing import TYPE_CHECKING, Any

from horey.jenkins_api.jenkins_api import JenkinsAPI
from horey.jenkins_api.jenkins_api_configuration_policy import JenkinsAPIConfigurationPolicy

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    :param registry: passed in by horey.mcp
    """

    @functools.cache
    def jenkins_api() -> JenkinsAPI:
        return JenkinsAPI(registry.get_configuration(JenkinsAPIConfigurationPolicy))

    @registry.tool(read_only=True)
    def get_build(job_name: str, build_number: int) -> dict[str, Any]:
        """Get a Jenkins build: result (None while building), building, duration, url."""
        info = jenkins_api().server.get_build_info(job_name, build_number)
        return {"result": info["result"], "building": info["building"]}

    @registry.tool()
    def trigger_job(job_name: str, parameters: dict[str, str] | None = None) -> int:
        """Trigger a Jenkins job. Returns the queue item id."""
        return jenkins_api().server.build_job(job_name, parameters or {})
```

Rules:

* The tool name is `<package_name>_<function name>`, e.g. `jenkins_api_get_build`.
* The docstring is the tool description and the type hints are the input schema. Claude sees only these.
* `read_only=True` for tools which do not change anything. `destructive=True` for tools which delete,
  overwrite or run commands.
* The package does not import `horey.mcp` at run time (only under `TYPE_CHECKING`, for the type hint).
  `mcp_tools.py` is imported only by the MCP server, so it adds no dependencies to the package.
* Create the API object lazily (`functools.cache`): the configuration is read on the first tool call,
  a missing configuration fails that call, not the server start.
* Sync tools run in a worker thread, they do not block the server. Still, return fast:
  trigger and return an id, let Claude poll a status tool. Don't wait for builds inside a tool.
* Return small results: a few fields, the last N log lines. Not raw API responses.
* Exceptions are returned to Claude as the tool error text (`<ExceptionType>: <message>`):
  the MCP SDK hides the text of other exceptions, the registry re-raises them as `ToolError`.
* A package failing to load is logged and skipped, the others are served.

Registry helpers:

| Helper | Use |
|--------|-----|
| `registry.get_configuration(PolicyClass)` | The package configuration policy, initialized from `<package_name>_configuration.py\|json` |
| `registry.get_configuration_file_path(file_name=None)` | Path of the package configuration, or of another file (e.g. an SSH key) in the configurations directory |
| `registry.to_jsonable(obj)` | horey objects to JSON: `dict_src` if the object has it, otherwise the public attributes |

## Packages exposing tools

`github_api`, `jenkins_api`, `infrastructure_api`, `provision_constructor`, `azure_api`, `chronograf_api`, `deployer`,
`docker_api`, `git_api`, `grafana_api`, `influxdb_api`, `kubernetes_api`, `opensearch_api`, `pip_api`, `postgres_api`,
`redis_api`, `replacement_engine`, `selenium_api`, `slack_api`, `zabbix_api`, `snyk_api`.
Call `mcp_list_packages` for the loaded packages and their tools.

What some of them need where the server runs:

| Package | Needs |
|---------|-------|
| `infrastructure_api` | AWS credentials in the container environment (`-e AWS_ACCESS_KEY_ID ...` or a role), `region` and `vpc_name` in its configuration |
| `docker_api` | The Docker socket: `-v /var/run/docker.sock:/var/run/docker.sock`. No configuration file |
| `deployer`, `provision_constructor` | SSH private keys as files in the configurations directory, passed by file name. `provision_constructor` also needs `deployer` in `HOREY_MCP_PACKAGES` |
| `git_api` | Works on the single repository of its configuration, cloned inside the container |
| `selenium_api` | Chrome, which the image does not include |
| `pip_api` | Nothing: without a configuration it lists the server's own packages |

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
