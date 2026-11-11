"""Tests for admissions-agent configuration, graph execution, and traces."""

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

import agents.admissions as admissions_module
from agents.admissions import AdmissionsAgent, AdmissionsAgentError


class FakeResearchTools:
    """Minimal per-run research state for isolated agent tests."""

    def __init__(self) -> None:
        self.tools = [object()]
        self.searches = 0
        self.retrievals = 0
        self.evidence: list[dict[str, Any]] = []
        self.trace: list[dict[str, Any]] = []


def configure_agent_mocks(
    monkeypatch: pytest.MonkeyPatch,
    graph: object,
    research_tools: FakeResearchTools,
    prompt_path: Path,
) -> dict[str, object]:
    """Patch model and graph construction so a test never contacts Ollama."""
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama.test:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")
    prompt_path.write_text("Test admissions system prompt", encoding="utf-8")
    monkeypatch.setattr(admissions_module, "SYSTEM_PROMPT_PATH", prompt_path)
    monkeypatch.setattr(admissions_module, "AdmissionsResearchTools", lambda: research_tools)
    model = object()
    model_arguments: dict[str, object] = {}

    def fake_chat_ollama(**kwargs: object) -> object:
        model_arguments.update(kwargs)
        return model

    graph_arguments: dict[str, object] = {}

    def fake_create_agent(**kwargs: object) -> object:
        graph_arguments.update(kwargs)
        return graph

    monkeypatch.setattr(admissions_module, "ChatOllama", fake_chat_ollama)
    monkeypatch.setattr(admissions_module, "create_agent", fake_create_agent)
    return {"model": model, "model_arguments": model_arguments, "graph_arguments": graph_arguments}


def test_agent_loads_prompt_from_file_on_initialization(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    prompt_path = tmp_path / "system_prompt.md"
    prompt_path.write_text("Admissions prompt from file", encoding="utf-8")
    monkeypatch.setattr(admissions_module, "SYSTEM_PROMPT_PATH", prompt_path)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama.test:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")

    agent = AdmissionsAgent()

    assert agent.system_prompt == "Admissions prompt from file"


def test_agent_rejects_missing_prompt_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(admissions_module, "SYSTEM_PROMPT_PATH", tmp_path / "missing.md")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama.test:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")

    with pytest.raises(AdmissionsAgentError, match="Could not load system prompt"):
        AdmissionsAgent()


def test_agent_runs_graph_reports_status_and_writes_trace(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    research_tools = FakeResearchTools()

    class FakeGraph:
        def invoke(self, state: dict[str, object], config: dict[str, Any]) -> dict[str, object]:
            assert state == {"messages": [{"role": "user", "content": "Compare admissions requirements"}]}
            assert config["recursion_limit"] == admissions_module.MAX_GRAPH_STEPS
            callback = config["callbacks"][0]
            callback.on_chat_model_start({}, [])
            callback.on_tool_start({"name": "web_search"}, "query")
            callback.on_tool_end("search result")
            callback.on_chat_model_start({}, [])
            return {"messages": [SimpleNamespace(content="Comparison answer with citations.")]}

    mock_state = configure_agent_mocks(
        monkeypatch,
        FakeGraph(),
        research_tools,
        tmp_path / "system_prompt.md",
    )
    statuses: list[tuple[str, str | None]] = []
    trace_path = tmp_path / "trace.json"

    answer = AdmissionsAgent().run(
        "Compare admissions requirements",
        trace_path=trace_path,
        status_callback=lambda event, value: statuses.append((event, value)),
    )
    trace = json.loads(trace_path.read_text(encoding="utf-8"))

    assert answer == "Comparison answer with citations."
    assert mock_state["model_arguments"] == {
        "model": "test-model",
        "base_url": "http://ollama.test:11434",
        "temperature": 0,
        "request_timeout": 300,
    }
    assert mock_state["graph_arguments"]["model"] is mock_state["model"]
    assert mock_state["graph_arguments"]["system_prompt"] == "Test admissions system prompt"
    assert statuses == [
        ("llm_start", None),
        ("tool_start", "web_search"),
        ("tool_end", None),
        ("llm_start", None),
    ]
    assert trace["question"] == "Compare admissions requirements"
    assert trace["answer"] == answer
    assert trace["action_count"] == 1
    assert trace["actions"][0]["action"] == "final_answer"


def test_agent_rejects_empty_question_before_creating_research_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama.test:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")

    with pytest.raises(AdmissionsAgentError, match="Please enter a research question"):
        AdmissionsAgent().run("   ")


def test_agent_records_graph_errors_in_trace(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    research_tools = FakeResearchTools()

    class FailingGraph:
        def invoke(self, state: dict[str, object], config: dict[str, Any]) -> dict[str, object]:
            raise RuntimeError("model unavailable")

    configure_agent_mocks(
        monkeypatch,
        FailingGraph(),
        research_tools,
        tmp_path / "system_prompt.md",
    )
    trace_path = tmp_path / "failed-trace.json"

    with pytest.raises(AdmissionsAgentError, match="Admissions research failed: model unavailable"):
        AdmissionsAgent().run("What are ASU's requirements?", trace_path=trace_path)

    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    assert trace["error"] == "model unavailable"
    assert trace["answer"] == ""
