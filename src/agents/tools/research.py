"""Live web search, page retrieval, and evidence tools for admissions research."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ddgs import DDGS
from ddgs.exceptions import DDGSException
from langchain_core.tools import tool

MAX_SEARCHES = 8
MAX_RETRIEVALS = 12
MAX_RESULTS = 8
MAX_PAGE_CHARS = 16000
REQUEST_TIMEOUT = 30


class AdmissionsResearchTools:
    """Create per-run tools and retain their evidence and action trace."""

    def __init__(self) -> None:
        self.searches = 0
        self.retrievals = 0
        self.evidence: list[dict[str, Any]] = []
        self.trace: list[dict[str, Any]] = []
        self.pages: dict[str, dict[str, Any]] = {}
        self.tools = self._build_tools()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _build_tools(self) -> list[Any]:
        @tool
        def web_search(query: str) -> str:
            """Search the live web. Returns ranked titles, URLs, snippets, and metadata."""
            query = query.strip()
            if not query:
                return "Error: search query must not be empty."
            if self.searches >= MAX_SEARCHES:
                return f"Search budget reached ({MAX_SEARCHES} calls)."
            self.searches += 1
            try:
                raw_results = DDGS().text(query, max_results=MAX_RESULTS, backend="duckduckgo")
            except DDGSException as error:
                result = {"error": f"DuckDuckGo search failed: {error}"}
                self.trace.append({"timestamp": self._now(), "action": "web_search", "query": query, **result})
                return json.dumps(result)
            results = [
                {
                    "rank": rank,
                    "title": item.get("title", ""),
                    "url": item.get("href", ""),
                    "snippet": item.get("body", ""),
                }
                for rank, item in enumerate(raw_results, start=1)
                if isinstance(item, dict) and item.get("href")
            ]
            self.trace.append(
                {"timestamp": self._now(), "action": "web_search", "query": query, "results": results}
            )
            return json.dumps(results, ensure_ascii=False)

        @tool
        def fetch_page(url: str) -> str:
            """Retrieve readable page text for a URL; page content, not snippets, is evidence."""
            url = url.strip()
            if not url.startswith(("https://", "http://")):
                return "Error: a valid HTTP(S) URL is required."
            if url in self.pages:
                return json.dumps(self.pages[url], ensure_ascii=False)
            if self.retrievals >= MAX_RETRIEVALS:
                return f"Retrieval budget reached ({MAX_RETRIEVALS} pages)."
            self.retrievals += 1
            jina_key = os.environ.get("JINA_API_KEY", "").strip()
            headers = {"Accept": "application/json", "X-Return-Format": "json"}
            if jina_key:
                headers["Authorization"] = f"Bearer {jina_key}"
            request = Request(f"https://r.jina.ai/{url}", headers=headers)
            try:
                with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                data = payload.get("data", payload) if isinstance(payload, dict) else {}
                if not isinstance(data, dict):
                    data = {}
                page = {
                    "title": data.get("title", ""),
                    "url": data.get("url", url),
                    "retrieval_timestamp": self._now(),
                    "content": str(data.get("content", ""))[:MAX_PAGE_CHARS],
                    "metadata": data.get("metadata", {}),
                }
            except (HTTPError, URLError, TimeoutError, OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
                page = {"url": url, "retrieval_timestamp": self._now(), "error": str(error), "content": ""}
            self.pages[url] = page
            self.trace.append({"timestamp": self._now(), "action": "fetch_page", **page})
            return json.dumps(page, ensure_ascii=False)

        @tool
        def save_evidence(
            claim: str,
            source_url: str,
            supporting_quote: str,
            source_quality: str,
            verification_label: str,
            verification_reason: str,
        ) -> str:
            """Store a claim with a passage from a page retrieved in this run and a verification label."""
            if source_url not in self.pages or not self.pages[source_url].get("content"):
                return "Evidence rejected: retrieve the source page successfully before citing it."
            if verification_label not in {"supported", "contradicted", "insufficient"}:
                return "Evidence rejected: label must be supported, contradicted, or insufficient."
            page = self.pages[source_url]
            if supporting_quote.strip() not in page.get("content", ""):
                return "Evidence rejected: the supporting quote must appear verbatim in the retrieved page text."
            record = {
                "claim": claim,
                "source_title": page.get("title", ""),
                "url": page.get("url", source_url),
                "retrieval_timestamp": page.get("retrieval_timestamp"),
                "supporting_quote": supporting_quote,
                "source_quality": source_quality,
                "verification_label": verification_label,
                "verification_reason": verification_reason,
            }
            self.evidence.append(record)
            self.trace.append({"timestamp": self._now(), "action": "save_evidence", "record": record})
            return json.dumps(record, ensure_ascii=False)

        @tool
        def list_evidence() -> str:
            """List the structured claim evidence collected in this research run."""
            return json.dumps(self.evidence, ensure_ascii=False)

        return [web_search, fetch_page, save_evidence, list_evidence]
