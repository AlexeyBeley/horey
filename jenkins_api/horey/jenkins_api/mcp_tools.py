"""
MCP tools of horey.jenkins_api. Loaded by horey.mcp, see mcp/README.md.
"""

from typing import TYPE_CHECKING, Any

from horey.jenkins_api.build import Build
from horey.jenkins_api.jenkins_api import JenkinsAPI
from horey.jenkins_api.jenkins_api_configuration_policy import JenkinsAPIConfigurationPolicy
from horey.jenkins_api.jenkins_job import JenkinsJob

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry

BUILD_FIELDS = ["number", "result", "building", "duration", "estimatedDuration", "timestamp", "url",
                "displayName", "description"]


def _build_number(build_src: dict[str, Any] | None) -> int | None:
    return build_src.get("number") if build_src else None


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    @registry.cached_per_configuration
    def jenkins_api(configuration_name: str | None) -> JenkinsAPI:
        return JenkinsAPI(registry.get_configuration(JenkinsAPIConfigurationPolicy, configuration_name))

    @registry.tool(read_only=True)
    def list_jobs(name_contains: str = "", configuration_name: str | None = None) -> list[dict[str, Any]]:
        """List all Jenkins jobs (including the ones in folders): fullname, url, color (status). Optional substring filter."""
        return [{"fullname": job.get("fullname"), "url": job.get("url"), "color": job.get("color")}
                for job in jenkins_api(configuration_name).get_all_jobs() if name_contains in job.get("fullname", "")]

    @registry.tool(read_only=True)
    def get_job_info(job_name: str, configuration_name: str | None = None) -> dict[str, Any]:
        """Get a Jenkins job: buildable, in queue, last/last successful/last failed build numbers and parameters."""
        info = jenkins_api(configuration_name).get_job_info(job_name)
        parameters = []
        for job_property in info.get("property", []):
            for definition in job_property.get("parameterDefinitions", []):
                parameters.append({"name": definition.get("name"), "type": definition.get("type"),
                                   "default": (definition.get("defaultParameterValue") or {}).get("value"),
                                   "description": definition.get("description")})
        return {"name": info.get("fullName") or info.get("name"), "url": info.get("url"),
                "buildable": info.get("buildable"), "in_queue": info.get("inQueue"), "color": info.get("color"),
                "last_build": _build_number(info.get("lastBuild")),
                "last_successful_build": _build_number(info.get("lastSuccessfulBuild")),
                "last_failed_build": _build_number(info.get("lastFailedBuild")),
                "next_build_number": info.get("nextBuildNumber"), "parameters": parameters}

    @registry.tool()
    def trigger_job(job_name: str, parameters: dict[str, str] | None = None,
                    configuration_name: str | None = None) -> dict[str, Any]:
        """
        Trigger a Jenkins job and return without waiting. Returns the queue item id:
        pass it to get_queue_item to get the build number once the build starts.
        """
        job = JenkinsJob(job_name, parameters or {})
        jenkins_api(configuration_name).thread_trigger_job(job)
        return {"job_name": job_name, "queue_item_id": job.queue_item_id}

    @registry.tool(read_only=True)
    def get_queue_item(queue_item_id: int, configuration_name: str | None = None) -> dict[str, Any]:
        """Get a queued build: why it waits, or the build number once it started (build_number is None until then)."""
        item = jenkins_api(configuration_name).server.get_queue_item(queue_item_id)
        executable = item.get("executable") or {}
        return {"queue_item_id": queue_item_id, "why": item.get("why"), "cancelled": item.get("cancelled"),
                "build_number": executable.get("number"), "build_url": executable.get("url")}

    @registry.tool(read_only=True)
    def get_build(job_name: str, build_number: int, configuration_name: str | None = None) -> dict[str, Any]:
        """Get a Jenkins build: result (None while building), building, duration, timestamp (ms), url."""
        info = jenkins_api(configuration_name).server.get_build_info(job_name, build_number)
        return {field: info.get(field) for field in BUILD_FIELDS}

    @registry.tool(read_only=True)
    def get_build_log(job_name: str, build_number: int, tail_lines: int = 200,
                      configuration_name: str | None = None) -> str:
        """Get the last tail_lines lines of a Jenkins build's console output."""
        build = Build({"name": job_name, "number": build_number})
        output = jenkins_api(configuration_name).get_build_console_output(build)
        return "\n".join(str(output).splitlines()[-tail_lines:])

    @registry.tool(read_only=True)
    def list_running_builds(configuration_name: str | None = None) -> list[dict[str, Any]]:
        """List the builds currently running on Jenkins executors."""
        return [{"job_name": build.name, "number": build.number, "url": build.url, "timestamp": build.timestamp}
                for build in jenkins_api(configuration_name).get_running_builds()]
