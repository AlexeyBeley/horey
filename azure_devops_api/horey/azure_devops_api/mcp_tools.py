"""
MCP tools of horey.azure_devops_api. Loaded by horey.mcp, see mcp/README.md.

Read-only access to the work items of the configured organisation, project and team.
The configuration (azure_devops_api_configuration[_<suffix>].py|json) holds the AzureDevopsAPIConfigurationPolicy
values: server_address, org_name, project_name, team_name, user and password (a personal access token
with the Work Items Read scope).
"""

import html.parser
from typing import TYPE_CHECKING, Any

from horey.azure_devops_api.azure_devops_api import AzureDevopsAPI, WorkItem
from horey.azure_devops_api.azure_devops_api_configuration_policy import AzureDevopsAPIConfigurationPolicy

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry

MAX_LIMIT = 1000

SUMMARY_FIELDS = ["System.Id", "System.WorkItemType", "System.Title", "System.State", "System.AssignedTo",
                  "System.IterationPath", "System.AreaPath", "System.Tags", "System.ChangedDate",
                  "Microsoft.VSTS.Common.Priority"]

DETAIL_FIELDS = {
    "reason": "System.Reason",
    "created_by": "System.CreatedBy",
    "created_date": "System.CreatedDate",
    "changed_by": "System.ChangedBy",
    "story_points": "Microsoft.VSTS.Scheduling.StoryPoints",
    "original_estimate": "Microsoft.VSTS.Scheduling.OriginalEstimate",
    "remaining_work": "Microsoft.VSTS.Scheduling.RemainingWork",
    "completed_work": "Microsoft.VSTS.Scheduling.CompletedWork",
    "comment_count": "System.CommentCount",
}

TEXT_FIELDS = {
    "description": "System.Description",
    "acceptance_criteria": "Microsoft.VSTS.Common.AcceptanceCriteria",
    "repro_steps": "Microsoft.VSTS.TCM.ReproSteps",
    "system_info": "Microsoft.VSTS.TCM.SystemInfo",
}

RELATION_NAMES = {
    "System.LinkTypes.Hierarchy-Reverse": "parent",
    "System.LinkTypes.Hierarchy-Forward": "children",
    "System.LinkTypes.Related": "related",
}


class _HTMLToText(html.parser.HTMLParser):
    """
    Work item rich text fields are HTML: keep the text and the line structure, drop the markup.
    """

    BLOCK_TAGS = {"p", "div", "br", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "pre", "blockquote", "ul", "ol",
                  "table"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")
        elif tag == "li":
            self.parts.append("\n- ")
        elif tag in ("td", "th"):
            self.parts.append(" | ")
        elif tag == "img":
            self.parts.append(f"[image: {dict(attrs).get('src') or ''}]")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str:
        """
        The collected text: lines stripped, repeated empty lines collapsed.
        """

        lines = [line.strip() for line in "".join(self.parts).replace("\xa0", " ").splitlines()]
        ret: list[str] = []
        for line in lines:
            if line or (ret and ret[-1]):
                ret.append(line)
        return "\n".join(ret).strip()


def html_to_text(value: Any) -> Any:
    """
    Plain text of an HTML field value. Other values are returned as is.
    """

    if not isinstance(value, str) or "<" not in value:
        return value
    parser = _HTMLToText()
    parser.feed(value)
    parser.close()
    return parser.text()


def _identity(value: Any) -> Any:
    """
    Identity fields (System.AssignedTo etc.) are dicts: the display name.
    """

    if isinstance(value, dict):
        return value.get("displayName") or value.get("uniqueName")
    return value


def wiql_string(value: str) -> str:
    """
    Quote a WIQL string literal.
    """

    return "'" + value.replace("'", "''") + "'"


def _relation_id(relation: dict[str, Any]) -> int | None:
    try:
        return int(relation["url"].rstrip("/").split("/")[-1])
    except (KeyError, ValueError):
        return None


# pylint: disable= too-many-statements, too-many-locals, too-many-arguments, too-many-positional-arguments
def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    @registry.cached_per_configuration
    def azure_devops_api(configuration_name: str | None) -> AzureDevopsAPI:
        return AzureDevopsAPI(registry.get_configuration(AzureDevopsAPIConfigurationPolicy, configuration_name))

    def web_url(api: AzureDevopsAPI, work_item_id: Any) -> str:
        return f"https://dev.azure.com/{api.org_name}/{api.project_name}/_workitems/edit/{work_item_id}"

    def summary(api: AzureDevopsAPI, work_item: WorkItem) -> dict[str, Any]:
        fields = work_item.fields
        tags = fields.get("System.Tags")
        return {"id": work_item.id, "type": fields.get("System.WorkItemType"), "title": fields.get("System.Title"),
                "state": fields.get("System.State"), "assigned_to": _identity(fields.get("System.AssignedTo")),
                "iteration_path": fields.get("System.IterationPath"), "area_path": fields.get("System.AreaPath"),
                "priority": fields.get("Microsoft.VSTS.Common.Priority"),
                "tags": [tag.strip() for tag in tags.split(";")] if tags else [],
                "changed_date": fields.get("System.ChangedDate"), "url": web_url(api, work_item.id)}

    def summaries(api: AzureDevopsAPI, work_item_ids: list[int]) -> list[dict[str, Any]]:
        return [summary(api, work_item) for work_item in api.get_work_items_batch(work_item_ids, fields=SUMMARY_FIELDS)]

    def check_limit(limit: int) -> int:
        if not 1 <= limit <= MAX_LIMIT:
            raise ValueError(f"limit must be between 1 and {MAX_LIMIT}")
        return limit

    @registry.tool(read_only=True)
    def search_work_items(title_contains: str = "", work_item_types: list[str] | None = None,
                          states: list[str] | None = None, assigned_to: str = "", iteration_path: str = "",
                          current_iteration: bool = False, area_path: str = "", tags: list[str] | None = None,
                          changed_since: str = "", limit: int = 50,
                          configuration_name: str | None = None) -> list[dict[str, Any]]:
        """
        Search the project's work items, most recently changed first. All the filters are optional and combined with AND.
        work_item_types: e.g. ["Bug", "User Story", "Task"]. states: e.g. ["New", "Active"].
        assigned_to: a display name, an email, or "@Me" for the configured user.
        iteration_path / area_path: the item is under this path, e.g. "project-horey\\Sprint 1".
        current_iteration: only the team's current iteration. changed_since: a date, e.g. "2026-01-31".
        Returns summaries: id, type, title, state, assigned_to, iteration and area paths, priority, tags, url.
        Read a single item with get_work_item.
        """
        conditions = ["[System.TeamProject] = @project"]
        if title_contains:
            conditions.append(f"[System.Title] CONTAINS {wiql_string(title_contains)}")
        if work_item_types:
            conditions.append(f"[System.WorkItemType] IN ({', '.join(wiql_string(value) for value in work_item_types)})")
        if states:
            conditions.append(f"[System.State] IN ({', '.join(wiql_string(value) for value in states)})")
        if assigned_to:
            conditions.append("[System.AssignedTo] = " + ("@Me" if assigned_to.lower() == "@me" else wiql_string(assigned_to)))
        if iteration_path:
            conditions.append(f"[System.IterationPath] UNDER {wiql_string(iteration_path)}")
        if current_iteration:
            conditions.append("[System.IterationPath] = @CurrentIteration")
        if area_path:
            conditions.append(f"[System.AreaPath] UNDER {wiql_string(area_path)}")
        for tag in tags or []:
            conditions.append(f"[System.Tags] CONTAINS {wiql_string(tag)}")
        if changed_since:
            conditions.append(f"[System.ChangedDate] >= {wiql_string(changed_since)}")

        wiql = ("SELECT [System.Id] FROM WorkItems WHERE " + " AND ".join(conditions)
                + " ORDER BY [System.ChangedDate] DESC")
        api = azure_devops_api(configuration_name)
        return summaries(api, api.query_work_item_ids(wiql, top=check_limit(limit)))

    @registry.tool(read_only=True)
    def query_work_items(wiql: str, limit: int = 50, configuration_name: str | None = None) -> list[dict[str, Any]]:
        """
        Run a WIQL query and return the summaries of the matching work items, in the query order.
        Runs in the team context: @project, @Me, @CurrentIteration, @Today macros work. Only the ids are used from the
        SELECT clause. E.g. "SELECT [System.Id] FROM WorkItems WHERE [System.TeamProject] = @project AND
        [System.WorkItemType] = 'Bug' AND [System.State] <> 'Closed' ORDER BY [Microsoft.VSTS.Common.Priority]".
        Prefer search_work_items for simple filters.
        """
        api = azure_devops_api(configuration_name)
        return summaries(api, api.query_work_item_ids(wiql, top=check_limit(limit)))

    @registry.tool(read_only=True)
    def get_work_item(work_item_id: int, include_all_fields: bool = False, max_text_chars: int = 20000,
                      configuration_name: str | None = None) -> dict[str, Any]:
        """
        Read a work item: the summary fields, description, acceptance criteria and repro steps as plain text,
        estimates, created/changed by, and its links: parent, children and related ids, other links
        (commits, pull requests, hyperlinks). include_all_fields adds every field, custom ones included.
        Comments are read with get_work_item_comments.
        """
        api = azure_devops_api(configuration_name)
        work_item = api.get_work_item(work_item_id)
        if "error" in work_item.dict_src:
            error = work_item.dict_src["error"]
            if isinstance(error, dict):
                error = error.get("message") or f"status code {error.get('status_code')}"
            raise RuntimeError(f"Work item {work_item_id} can not be read: {error}")

        ret = summary(api, work_item)
        fields = work_item.fields
        for key, field_name in DETAIL_FIELDS.items():
            if field_name in fields:
                ret[key] = _identity(fields[field_name])
        for key, field_name in TEXT_FIELDS.items():
            if fields.get(field_name):
                text = html_to_text(fields[field_name])
                ret[key] = text[:max_text_chars] + ("\n[truncated]" if len(text) > max_text_chars else "")

        relations: dict[str, Any] = {"parent": None, "children": [], "related": [], "other_links": []}
        for relation in work_item.relations or []:
            name = RELATION_NAMES.get(relation.get("rel", ""))
            if name == "parent":
                relations["parent"] = _relation_id(relation)
            elif name:
                relations[name].append(_relation_id(relation))
            else:
                attributes = relation.get("attributes") or {}
                relations["other_links"].append({"type": attributes.get("name") or relation.get("rel"),
                                                 "url": relation.get("url"),
                                                 "comment": attributes.get("comment")})
        ret.update(relations)

        if include_all_fields:
            ret["all_fields"] = {name: _identity(html_to_text(value)) for name, value in fields.items()}
        return ret

    @registry.tool(read_only=True)
    def get_work_items(work_item_ids: list[int], configuration_name: str | None = None) -> list[dict[str, Any]]:
        """
        Get the summaries of several work items by id, e.g. the children of an item from get_work_item.
        Ids which do not exist or are not accessible are skipped.
        """
        if len(work_item_ids) > MAX_LIMIT:
            raise ValueError(f"At most {MAX_LIMIT} ids")
        return summaries(azure_devops_api(configuration_name), work_item_ids)

    @registry.tool(read_only=True)
    def get_work_item_comments(work_item_id: int, limit: int = 50,
                               configuration_name: str | None = None) -> list[dict[str, Any]]:
        """Read the discussion comments of a work item as plain text: id, author, created and modified dates, text."""
        comments = azure_devops_api(configuration_name).get_wit_comments(work_item_id)
        return [{"id": comment.get("id"), "author": _identity(comment.get("createdBy")),
                 "created_date": comment.get("createdDate"), "modified_date": comment.get("modifiedDate"),
                 "text": html_to_text(comment.get("text"))}
                for comment in comments[:check_limit(limit)]]

    @registry.tool(read_only=True)
    def list_iterations(timeframe: str = "", configuration_name: str | None = None) -> list[dict[str, Any]]:
        """
        List the team's iterations (sprints): name, path (use as iteration_path in search_work_items), start and
        finish dates, timeframe. timeframe filters by "past", "current" or "future".
        """
        return [{"name": iteration.get("name"), "path": iteration.get("path"),
                 "start_date": (iteration.get("attributes") or {}).get("startDate"),
                 "finish_date": (iteration.get("attributes") or {}).get("finishDate"),
                 "timeframe": (iteration.get("attributes") or {}).get("timeFrame")}
                for iteration in azure_devops_api(configuration_name).get_team_iterations()
                if not timeframe or (iteration.get("attributes") or {}).get("timeFrame") == timeframe.lower()]
