"""
Testing horey.azure_devops_api MCP tools with a fake Azure DevOps REST API.
"""

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import CallToolResult

from horey.azure_devops_api import azure_devops_api as azure_devops_api_module
from horey.azure_devops_api.mcp_tools import html_to_text, register_mcp_tools, wiql_string
from horey.mcp.mcp_tools_registry import MCPToolsRegistry

# pylint: disable= missing-function-docstring

CONFIGURATION = {"server_address": "https://dev.azure.com", "user": "user-horey", "password": "token-horey",
                 "org_name": "org-horey", "project_name": "project-horey", "team_name": "team horey"}

WORK_ITEM = {
    "id": 101,
    "fields": {
        "System.Id": 101,
        "System.WorkItemType": "User Story",
        "System.Title": "Title horey",
        "System.State": "Active",
        "System.AssignedTo": {"displayName": "User Horey", "uniqueName": "user-horey@horey.com"},
        "System.IterationPath": "project-horey\\Sprint 1",
        "System.AreaPath": "project-horey",
        "System.Tags": "tag-horey; backend",
        "System.ChangedDate": "2026-01-02T00:00:00Z",
        "System.CreatedBy": {"displayName": "Creator Horey"},
        "Microsoft.VSTS.Scheduling.StoryPoints": 3.0,
        "System.Description": "<div>First line</div><ul><li>item &amp; one</li><li>item two</li></ul>",
        "Custom.HoreyField": "custom-horey",
    },
    "relations": [
        {"rel": "System.LinkTypes.Hierarchy-Reverse", "url": "https://horey.com/_apis/wit/workItems/100",
         "attributes": {"name": "Parent"}},
        {"rel": "System.LinkTypes.Hierarchy-Forward", "url": "https://horey.com/_apis/wit/workItems/102",
         "attributes": {"name": "Child"}},
        {"rel": "System.LinkTypes.Hierarchy-Forward", "url": "https://horey.com/_apis/wit/workItems/103",
         "attributes": {"name": "Child"}},
        {"rel": "ArtifactLink", "url": "vstfs:///Git/PullRequestId/horey", "attributes": {"name": "Pull Request"}},
    ],
}


class FakeResponse:
    """
    requests.Response replacement.
    """

    def __init__(self, status_code: int, body: Any) -> None:
        self.status_code = status_code
        self.body = body
        self.text = json.dumps(body)
        self.headers: dict[str, str] = {}

    def json(self) -> Any:
        return self.body


class FakeSession:
    """
    requests.Session replacement answering the endpoints the tools use.
    """

    requests: list[tuple[str, str, Any]] = []

    def __init__(self) -> None:
        self.auth = None
        self.headers: dict[str, str] = {}

    def get(self, url: str) -> FakeResponse:
        FakeSession.requests.append(("GET", url, None))
        if "/_apis/wit/workitems/404" in url:
            return FakeResponse(404, {"message": "TF401232: Work item 404 does not exist"})
        if "/_apis/wit/workitems/101/comments" in url:
            return FakeResponse(200, {"totalCount": 1, "count": 1, "comments": [
                {"id": 1, "createdBy": {"displayName": "User Horey"}, "createdDate": "2026-01-03T00:00:00Z",
                 "text": "<p>Looks <b>good</b></p>"}]})
        if "/_apis/wit/workitems/101" in url:
            return FakeResponse(200, WORK_ITEM)
        if "/_apis/work/teamsettings/iterations" in url:
            return FakeResponse(200, {"value": [
                {"name": "Sprint 1", "path": "project-horey\\Sprint 1",
                 "attributes": {"startDate": "2026-01-01T00:00:00Z", "finishDate": "2026-01-14T00:00:00Z",
                                "timeFrame": "current"}},
                {"name": "Sprint 2", "path": "project-horey\\Sprint 2", "attributes": {"timeFrame": "future"}}]})
        raise AssertionError(f"Unexpected GET {url}")

    def post(self, url: str, json: Any = None, headers: Any = None) -> FakeResponse:  # pylint: disable=redefined-outer-name
        FakeSession.requests.append(("POST", url, json))
        assert headers == {"Content-Type": "application/json"}
        if "/_apis/wit/wiql" in url:
            if "INVALID" in json["query"]:
                return FakeResponse(400, {"message": "TF51005: The query references a field that does not exist"})
            return FakeResponse(200, {"queryType": "flat", "workItems": [{"id": 101}, {"id": 102}]})
        if "/_apis/wit/workitemsbatch" in url:
            return FakeResponse(200, {"value": [{"id": work_item_id, "fields": {
                **{name: value for name, value in WORK_ITEM["fields"].items() if name in json["fields"]},
                "System.Id": work_item_id}} for work_item_id in json["ids"]]})
        raise AssertionError(f"Unexpected POST {url}")


@pytest.fixture(name="mcp_server")
def fixture_mcp_server(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> MCPServer:
    (tmp_path / "azure_devops_api_configuration_dev_horey.json").write_text(json.dumps(CONFIGURATION))
    monkeypatch.setattr(azure_devops_api_module.requests, "Session", FakeSession)
    FakeSession.requests = []
    mcp_server = MCPServer("horey")
    register_mcp_tools(MCPToolsRegistry(mcp_server, "azure_devops_api", tmp_path))
    return mcp_server


def call(mcp_server: MCPServer, tool_name: str, arguments: dict[str, Any]) -> Any:
    result = asyncio.run(mcp_server.call_tool(f"azure_devops_api_{tool_name}", arguments))
    assert isinstance(result, CallToolResult)
    assert not result.is_error
    assert result.structured_content is not None
    # Lists are wrapped in {"result": ...}, dicts are returned as is.
    if set(result.structured_content) == {"result"}:
        return result.structured_content["result"]
    return result.structured_content


@pytest.mark.unit
def test_tools_registered(mcp_server: MCPServer) -> None:
    tool_names = {tool.name for tool in asyncio.run(mcp_server.list_tools())}
    assert tool_names == {f"azure_devops_api_{name}" for name in [
        "list_configurations", "search_work_items", "query_work_items", "get_work_item", "get_work_items",
        "get_work_item_comments", "list_iterations"]}


@pytest.mark.unit
def test_search_work_items(mcp_server: MCPServer) -> None:
    items = call(mcp_server, "search_work_items", {
        "title_contains": "horey's", "work_item_types": ["Bug", "User Story"], "states": ["Active"],
        "assigned_to": "@me", "current_iteration": True, "tags": ["tag-horey"], "limit": 10})

    _, wiql_url, wiql_body = FakeSession.requests[0]
    assert wiql_url.startswith("https://dev.azure.com/org-horey/project-horey/team%20horey/_apis/wit/wiql?")
    assert wiql_url.endswith("&$top=10")
    query = wiql_body["query"]
    assert "[System.Title] CONTAINS 'horey''s'" in query
    assert "[System.WorkItemType] IN ('Bug', 'User Story')" in query
    assert "[System.AssignedTo] = @Me" in query
    assert "[System.IterationPath] = @CurrentIteration" in query
    assert "[System.Tags] CONTAINS 'tag-horey'" in query
    assert query.endswith("ORDER BY [System.ChangedDate] DESC")

    _, batch_url, batch_body = FakeSession.requests[1]
    assert "/_apis/wit/workitemsbatch" in batch_url
    assert batch_body["ids"] == [101, 102]
    assert [item["id"] for item in items] == [101, 102]
    assert items[0] == {"id": 101, "type": "User Story", "title": "Title horey", "state": "Active",
                        "assigned_to": "User Horey", "iteration_path": "project-horey\\Sprint 1",
                        "area_path": "project-horey", "priority": None, "tags": ["tag-horey", "backend"],
                        "changed_date": "2026-01-02T00:00:00Z",
                        "url": "https://dev.azure.com/org-horey/project-horey/_workitems/edit/101"}


@pytest.mark.unit
def test_query_work_items_error_reaches_client(mcp_server: MCPServer) -> None:
    with pytest.raises(ToolError, match="TF51005"):
        asyncio.run(mcp_server.call_tool("azure_devops_api_query_work_items",
                                         {"wiql": "SELECT [System.Id] FROM WorkItems WHERE INVALID"}))


@pytest.mark.unit
def test_get_work_item(mcp_server: MCPServer) -> None:
    item = call(mcp_server, "get_work_item", {"work_item_id": 101, "include_all_fields": True})
    assert item["title"] == "Title horey"
    assert item["description"] == "First line\n\n- item & one\n- item two"
    assert item["created_by"] == "Creator Horey"
    assert item["story_points"] == 3.0
    assert item["parent"] == 100
    assert item["children"] == [102, 103]
    assert item["related"] == []
    assert item["other_links"] == [{"type": "Pull Request", "url": "vstfs:///Git/PullRequestId/horey",
                                    "comment": None}]
    assert item["all_fields"]["Custom.HoreyField"] == "custom-horey"


@pytest.mark.unit
def test_get_work_item_missing(mcp_server: MCPServer) -> None:
    with pytest.raises(ToolError, match="Work item 404 can not be read: TF401232"):
        asyncio.run(mcp_server.call_tool("azure_devops_api_get_work_item", {"work_item_id": 404}))


@pytest.mark.unit
def test_get_work_items_and_comments(mcp_server: MCPServer) -> None:
    assert [item["id"] for item in call(mcp_server, "get_work_items", {"work_item_ids": [102, 103]})] == [102, 103]
    comments = call(mcp_server, "get_work_item_comments", {"work_item_id": 101})
    assert comments == [{"id": 1, "author": "User Horey", "created_date": "2026-01-03T00:00:00Z",
                         "modified_date": None, "text": "Looks good"}]


@pytest.mark.unit
def test_list_iterations(mcp_server: MCPServer) -> None:
    assert [iteration["name"] for iteration in call(mcp_server, "list_iterations", {})] == ["Sprint 1", "Sprint 2"]
    current = call(mcp_server, "list_iterations", {"timeframe": "current"})
    assert current == [{"name": "Sprint 1", "path": "project-horey\\Sprint 1", "start_date": "2026-01-01T00:00:00Z",
                        "finish_date": "2026-01-14T00:00:00Z", "timeframe": "current"}]


@pytest.mark.unit
def test_limit_validated(mcp_server: MCPServer) -> None:
    with pytest.raises(ToolError, match="limit must be between"):
        asyncio.run(mcp_server.call_tool("azure_devops_api_search_work_items", {"limit": 0}))


@pytest.mark.unit
def test_html_to_text() -> None:
    assert html_to_text("plain horey") == "plain horey"
    assert html_to_text(None) is None
    assert html_to_text("<p>a&nbsp;b</p><br><table><tr><td>x</td><td>y</td></tr></table>") == "a b\n\n| x | y"
    assert wiql_string("o'horey") == "'o''horey'"
