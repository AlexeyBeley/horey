"""
MCP tools of horey.selenium_api. Loaded by horey.mcp, see mcp/README.md.
Needs Chrome where the server runs: the default horey MCP image does not include it.
A single browser is shared by all the calls.
"""

import functools
import threading
from typing import TYPE_CHECKING, Any

from selenium.webdriver.common.by import By

from horey.selenium_api.selenium_api import SeleniumAPI

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    browser_lock = threading.Lock()

    @functools.cache
    def selenium_api() -> SeleniumAPI:
        return SeleniumAPI()

    @registry.tool(read_only=True)
    def get_page_text(url: str, max_chars: int = 20000) -> dict[str, Any]:
        """Open a URL in Chrome (JavaScript rendered) and return the page title, final URL and visible text."""
        with browser_lock:
            api = selenium_api()
            api.get(url)
            api.wait_for_page_load()
            driver = SeleniumAPI.driver
            if driver is None:
                raise RuntimeError("Chrome driver is not connected")
            text = driver.find_element(By.TAG_NAME, "body").text
            return {"title": driver.title, "url": driver.current_url,
                    "text": text[:max_chars], "truncated": len(text) > max_chars}

    @registry.tool(read_only=True)
    def get_page_links(url: str, limit: int = 200) -> list[dict[str, str]]:
        """Open a URL in Chrome (JavaScript rendered) and return its links: text and href."""
        with browser_lock:
            api = selenium_api()
            api.get(url)
            api.wait_for_page_load()
            links = []
            for element in api.get_elements_by_tagname("a"):
                href = element.get_attribute("href")
                if href:
                    links.append({"text": element.text.strip(), "href": href})
                if len(links) >= limit:
                    break
            return links
