"""Tests for the Brave Search and Jina Reader tool."""

import io
import json
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request

import pytest
from langchain_core.tools import ToolException

import agents.brave_jina_search as brave_jina_search
from agents.brave_jina_search import BraveJinaSearchResults


def json_response(data: dict[str, object]) -> io.BytesIO:
    return io.BytesIO(json.dumps(data).encode("utf-8"))


def test_search_returns_brave_results_with_jina_content(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BRAVE_API_KEY", "brave-test-key")
    monkeypatch.delenv("JINA_API_KEY", raising=False)
    requests: list[Request] = []

    def fake_urlopen(request: Request, timeout: int) -> io.BytesIO:
        requests.append(request)
        if "api.search.brave.com" in request.full_url:
            return json_response(
                {
                    "web": {
                        "results": [
                            {
                                "title": "Example Result",
                                "url": "https://example.com/article",
                                "description": "Search snippet",
                            }
                        ]
                    }
                }
            )
        return json_response(
            {
                "data": {
                    "title": "Retrieved Page",
                    "url": "https://example.com/article",
                    "content": "Full page text",
                }
            }
        )

    monkeypatch.setattr(brave_jina_search, "urlopen", fake_urlopen)

    result = json.loads(BraveJinaSearchResults(max_results=3).invoke({"query": "example query"}))

    assert len(requests) == 2
    brave_request = requests[0]
    assert parse_qs(urlparse(brave_request.full_url).query) == {"q": ["example query"], "count": ["3"]}
    assert brave_request.get_header("X-subscription-token") == "brave-test-key"
    assert "https://r.jina.ai/https://example.com/article" == requests[1].full_url
    assert result == [
        {
            "title": "Retrieved Page",
            "url": "https://example.com/article",
            "content": "Full page text",
            "snippet": "Search snippet",
        }
    ]


def test_reader_error_is_attached_to_search_result(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BRAVE_API_KEY", "brave-test-key")
    search_response = json_response(
        {"web": {"results": [{"title": "Example", "url": "https://example.com", "description": "Snippet"}]}}
    )

    def fake_urlopen(request: Request, timeout: int) -> io.BytesIO:
        if "api.search.brave.com" in request.full_url:
            return search_response
        raise HTTPError(request.full_url, 503, "Service Unavailable", None, io.BytesIO(b"reader unavailable"))

    monkeypatch.setattr(brave_jina_search, "urlopen", fake_urlopen)

    results = json.loads(BraveJinaSearchResults().invoke({"query": "example"}))

    assert len(results) == 1
    assert results[0]["url"] == "https://example.com"
    assert results[0]["content"] == ""
    assert "HTTP 503" in results[0]["reader_error"]


def test_search_requires_brave_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BRAVE_API_KEY", raising=False)

    with pytest.raises(ToolException, match="Set BRAVE_API_KEY"):
        BraveJinaSearchResults().invoke({"query": "example"})
