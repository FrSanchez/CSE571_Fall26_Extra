"""LangChain search tool backed by Brave Search and Jina Reader."""

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool, ToolException

BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"
JINA_READER_URL = "https://r.jina.ai/"
REQUEST_TIMEOUT = 30
MAX_CONTENT_CHARS = 8000


def _read_json(url: str, headers: dict[str, str], provider: str) -> dict[str, Any]:
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = error.read(512).decode("utf-8", errors="replace").strip()
        suffix = f": {detail}" if detail else ""
        raise ToolException(f"{provider} request failed with HTTP {error.code}{suffix}.") from error
    except (URLError, TimeoutError, OSError) as error:
        raise ToolException(f"{provider} request failed: {error}.") from error
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ToolException(f"{provider} returned invalid JSON.") from error
    if not isinstance(data, dict):
        raise ToolException(f"{provider} returned an unexpected response.")
    return data


class BraveJinaSearchResults(BaseTool):
    """Search Brave and retrieve readable content from each matching page."""

    name: str = "brave_jina_search"
    description: str = (
        "Search the web and retrieve readable page content for the top results. "
        "Use this for current factual research and cite the returned URLs."
    )
    max_results: int = 5

    def _run(
        self,
        query: str,
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> str:
        """Return JSON records with each result's title, URL, snippet, and page content."""
        query = query.strip()
        if not query:
            raise ToolException("Search query must not be empty.")
        if not 1 <= self.max_results <= 20:
            raise ToolException("max_results must be between 1 and 20.")

        brave_key = os.environ.get("BRAVE_API_KEY", "").strip()
        if not brave_key:
            raise ToolException("Set BRAVE_API_KEY to use Brave Search.")

        brave_data = _read_json(
            f"{BRAVE_SEARCH_URL}?{urlencode({'q': query, 'count': self.max_results})}",
            {
                "Accept": "application/json",
                "X-Subscription-Token": brave_key,
            },
            "Brave Search",
        )
        web_data = brave_data.get("web")
        web_results = web_data.get("results", []) if isinstance(web_data, dict) else []
        if not isinstance(web_results, list):
            raise ToolException("Brave Search returned results in an unexpected format.")

        jina_key = os.environ.get("JINA_API_KEY", "").strip()
        results: list[dict[str, str]] = []
        for item in web_results[: self.max_results]:
            if not isinstance(item, dict):
                continue
            title = item.get("title", "")
            page_url = item.get("url", "")
            snippet = item.get("description", "")
            if not isinstance(page_url, str) or not page_url:
                continue

            headers = {"Accept": "application/json"}
            if jina_key:
                headers["Authorization"] = f"Bearer {jina_key}"
            try:
                page_data = _read_json(f"{JINA_READER_URL}{page_url}", headers, "Jina Reader")
                page = page_data.get("data", page_data)
                content = page.get("content", "") if isinstance(page, dict) else ""
                if not isinstance(content, str):
                    content = ""
                results.append(
                    {
                        "title": str(page.get("title") or title),
                        "url": str(page.get("url") or page_url),
                        "content": content[:MAX_CONTENT_CHARS],
                        "snippet": str(snippet),
                    }
                )
            except ToolException as error:
                results.append(
                    {
                        "title": str(title),
                        "url": page_url,
                        "content": "",
                        "snippet": str(snippet),
                        "reader_error": str(error),
                    }
                )

        return json.dumps(results)
