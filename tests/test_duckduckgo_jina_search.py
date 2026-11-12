"""Tests for the DuckDuckGo and Jina Reader tool."""

import io
import json
from urllib.error import HTTPError
from urllib.request import Request

from ddgs.exceptions import DDGSException
import pytest
from langchain_core.tools import ToolException

import agents.duckduckgo_jina_search as duckduckgo_jina_search
from agents.duckduckgo_jina_search import DuckDuckGoJinaSearchResults


def json_response(data: dict[str, object]) -> io.BytesIO:
    return io.BytesIO(json.dumps(data).encode("utf-8"))


def test_search_returns_duckduckgo_results_with_jina_content(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BRAVE_API_KEY", raising=False)
    monkeypatch.delenv("JINA_API_KEY", raising=False)
    requests: list[Request] = []

    class FakeDDGS:
        def text(self, query: str, max_results: int, backend: str) -> list[dict[str, str]]:
            assert query == "example query"
            assert max_results == 3
            assert backend == "duckduckgo"
            return [
                {
                    "title": "Example Result",
                    "href": "https://example.com/article",
                    "body": "Search snippet",
                }
            ]

    def fake_urlopen(request: Request, timeout: int) -> io.BytesIO:
        requests.append(request)
        return json_response(
            {
                "data": {
                    "title": "Retrieved Page",
                    "url": "https://example.com/article",
                    "content": "Full page text",
                }
            }
        )

    monkeypatch.setattr(duckduckgo_jina_search, "DDGS", FakeDDGS)
    monkeypatch.setattr(duckduckgo_jina_search, "urlopen", fake_urlopen)

    result = json.loads(DuckDuckGoJinaSearchResults(max_results=3).invoke({"query": "example query"}))

    assert len(requests) == 1
    assert requests[0].full_url == "https://r.jina.ai/https://example.com/article"
    assert result == [
        {
            "title": "Retrieved Page",
            "url": "https://example.com/article",
            "content": "Full page text",
            "snippet": "Search snippet",
        }
    ]


def test_reader_error_is_attached_to_search_result(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeDDGS:
        def text(self, query: str, max_results: int, backend: str) -> list[dict[str, str]]:
            return [{"title": "Example", "href": "https://example.com", "body": "Snippet"}]

    def fake_urlopen(request: Request, timeout: int) -> io.BytesIO:
        raise HTTPError(request.full_url, 503, "Service Unavailable", None, io.BytesIO(b"reader unavailable"))

    monkeypatch.setattr(duckduckgo_jina_search, "DDGS", FakeDDGS)
    monkeypatch.setattr(duckduckgo_jina_search, "urlopen", fake_urlopen)

    results = json.loads(DuckDuckGoJinaSearchResults().invoke({"query": "example"}))

    assert len(results) == 1
    assert results[0]["url"] == "https://example.com"
    assert results[0]["content"] == ""
    assert "HTTP 503" in results[0]["reader_error"]


def test_search_wraps_duckduckgo_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeDDGS:
        def text(self, query: str, max_results: int, backend: str) -> list[dict[str, str]]:
            raise DDGSException("search unavailable")

    monkeypatch.setattr(duckduckgo_jina_search, "DDGS", FakeDDGS)

    with pytest.raises(ToolException, match="DuckDuckGo search failed"):
        DuckDuckGoJinaSearchResults().invoke({"query": "example"})
