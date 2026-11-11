"""Tests for the admissions web-search, retrieval, and evidence tools."""

import io
import json
from urllib.error import HTTPError
from urllib.request import Request

import pytest

import agents.tools.research as research_module
from agents.tools import AdmissionsResearchTools


def json_response(data: dict[str, object]) -> io.BytesIO:
    """Build a file-like JSON response for mocked HTTP requests."""
    return io.BytesIO(json.dumps(data).encode("utf-8"))


def get_tool(research_tools: AdmissionsResearchTools, name: str) -> object:
    """Look up one LangChain tool by its exposed name."""
    return next(tool for tool in research_tools.tools if tool.name == name)


def test_web_search_returns_ranked_results_and_trace(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeDDGS:
        def text(self, query: str, max_results: int, backend: str) -> list[dict[str, str]]:
            assert query == "ASU first year admissions"
            assert max_results == research_module.MAX_RESULTS
            assert backend == "duckduckgo"
            return [
                {"title": "ASU Admissions", "href": "https://admission.asu.edu/", "body": "First-year criteria"},
                {"title": "ASU Catalog", "href": "https://catalog.asu.edu/", "body": "Published policy"},
            ]

    monkeypatch.setattr(research_module, "DDGS", FakeDDGS)
    research_tools = AdmissionsResearchTools()

    results = json.loads(get_tool(research_tools, "web_search").invoke({"query": "ASU first year admissions"}))

    assert [item["rank"] for item in results] == [1, 2]
    assert results[0]["url"] == "https://admission.asu.edu/"
    assert research_tools.searches == 1
    assert research_tools.trace[0]["action"] == "web_search"


def test_web_search_enforces_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = 0

    class FakeDDGS:
        def text(self, query: str, max_results: int, backend: str) -> list[dict[str, str]]:
            nonlocal calls
            calls += 1
            return []

    monkeypatch.setattr(research_module, "DDGS", FakeDDGS)
    research_tools = AdmissionsResearchTools()
    search_tool = get_tool(research_tools, "web_search")

    for _ in range(research_module.MAX_SEARCHES):
        search_tool.invoke({"query": "ASU admissions"})
    last_result = search_tool.invoke({"query": "ASU admission deadline"})

    assert "budget reached" in last_result
    assert calls == research_module.MAX_SEARCHES
    assert research_tools.searches == research_module.MAX_SEARCHES


def test_fetch_page_records_retrieved_text_and_evidence(monkeypatch: pytest.MonkeyPatch) -> None:
    page_url = "https://admission.asu.edu/first-year/apply"

    def fake_urlopen(request: Request, timeout: int) -> io.BytesIO:
        assert request.full_url == f"https://r.jina.ai/{page_url}"
        assert timeout == research_module.REQUEST_TIMEOUT
        return json_response(
            {
                "data": {
                    "title": "ASU First-Year Admission",
                    "url": page_url,
                    "content": "Applicants must meet the published competency requirements.",
                    "metadata": {"publishedTime": "2026-01-01"},
                }
            }
        )

    monkeypatch.setattr(research_module, "urlopen", fake_urlopen)
    research_tools = AdmissionsResearchTools()
    fetch_tool = get_tool(research_tools, "fetch_page")

    page = json.loads(fetch_tool.invoke({"url": page_url}))
    record = json.loads(
        get_tool(research_tools, "save_evidence").invoke(
            {
                "claim": "ASU publishes competency requirements.",
                "source_url": page_url,
                "supporting_quote": "Applicants must meet the published competency requirements.",
                "source_quality": "Official ASU admissions source",
                "verification_label": "supported",
                "verification_reason": "The passage states the requirement directly.",
            }
        )
    )
    evidence = json.loads(get_tool(research_tools, "list_evidence").invoke({}))

    assert page["title"] == "ASU First-Year Admission"
    assert page["content"].startswith("Applicants must meet")
    assert page["retrieval_timestamp"]
    assert record["url"] == page_url
    assert record["verification_label"] == "supported"
    assert evidence == [record]
    assert research_tools.retrievals == 1


def test_save_evidence_rejects_unretrieved_pages_and_inexact_quotes() -> None:
    research_tools = AdmissionsResearchTools()
    save_tool = get_tool(research_tools, "save_evidence")
    arguments = {
        "claim": "ASU has an admissions requirement.",
        "source_url": "https://admission.asu.edu/",
        "supporting_quote": "A purported quote",
        "source_quality": "Official source",
        "verification_label": "supported",
        "verification_reason": "Direct statement.",
    }

    not_retrieved = save_tool.invoke(arguments)
    research_tools.pages[arguments["source_url"]] = {"content": "Actual page passage"}
    quote_not_found = save_tool.invoke(arguments)

    assert "retrieve the source page" in not_retrieved
    assert "must appear verbatim" in quote_not_found
    assert research_tools.evidence == []


def test_save_evidence_rejects_invalid_verification_label() -> None:
    research_tools = AdmissionsResearchTools()
    page_url = "https://admission.asu.edu/"
    research_tools.pages[page_url] = {"content": "Exact source passage"}
    result = get_tool(research_tools, "save_evidence").invoke(
        {
            "claim": "A claim",
            "source_url": page_url,
            "supporting_quote": "Exact source passage",
            "source_quality": "Official source",
            "verification_label": "probably true",
            "verification_reason": "Unclear label.",
        }
    )

    assert "label must be" in result
    assert research_tools.evidence == []


def test_fetch_page_records_http_error_without_creating_evidence(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_http_error(request: Request, timeout: int) -> io.BytesIO:
        raise HTTPError(request.full_url, 503, "Unavailable", None, io.BytesIO(b"reader down"))

    monkeypatch.setattr(research_module, "urlopen", raise_http_error)
    research_tools = AdmissionsResearchTools()
    page_url = "https://admission.asu.edu/"

    page = json.loads(get_tool(research_tools, "fetch_page").invoke({"url": page_url}))
    evidence_result = get_tool(research_tools, "save_evidence").invoke(
        {
            "claim": "A claim",
            "source_url": page_url,
            "supporting_quote": "Any quote",
            "source_quality": "Official source",
            "verification_label": "supported",
            "verification_reason": "Reason",
        }
    )

    assert "error" in page
    assert page["content"] == ""
    assert "retrieve the source page" in evidence_result
    assert research_tools.retrievals == 1
