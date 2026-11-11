"""LangGraph-backed evidence-seeking research agent for ASU admissions."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from typing import Any, Callable

from langchain.agents import create_agent
from langchain_core.callbacks import BaseCallbackHandler
from langchain_ollama import ChatOllama

from agents.tools import AdmissionsResearchTools

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen3.5:9b"
MAX_GRAPH_STEPS = 50
TRACE_DIR = Path("runs")
SYSTEM_PROMPT_PATH = Path(__file__).with_name("system_prompt.md")


class AdmissionsAgentError(Exception):
    """Raised for invalid questions or failures from the research agent."""


class AgentStatusCallbackHandler(BaseCallbackHandler):
    """Report active tool names while the graph runs, and clear them between calls."""

    def __init__(self, status_callback: Callable[[str, str | None], None]) -> None:
        self.status_callback = status_callback

    def on_llm_start(self, serialized: dict[str, Any], prompts: list[str], **kwargs: Any) -> None:
        """Signal that a new model response is starting."""
        self.status_callback("llm_start", None)

    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[Any]],
        **kwargs: Any,
    ) -> None:
        """Signal that a new chat-model response is starting."""
        self.status_callback("llm_start", None)

    def on_tool_start(self, serialized: dict[str, Any], input_str: str, **kwargs: Any) -> None:
        """Publish the name of the tool currently running."""
        tool_name = serialized.get("name", "research tool")
        self.status_callback("tool_start", str(tool_name))

    def on_tool_end(self, output: Any, **kwargs: Any) -> None:
        """Clear the running-tool status when a tool finishes."""
        self.status_callback("tool_end", None)

    def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        """Clear the running-tool status when a tool fails."""
        self.status_callback("tool_end", None)


class AdmissionsAgent:
    """Run an ASU admissions research question through a LangGraph agent."""

    def __init__(self) -> None:
        self.base_url = os.environ.get("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).rstrip("/")
        self.model_name = os.environ.get("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL).strip()
        if not self.base_url or not self.model_name:
            raise AdmissionsAgentError("OLLAMA_BASE_URL and OLLAMA_MODEL must be non-empty.")
        try:
            self.system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()
        except OSError as error:
            raise AdmissionsAgentError(f"Could not load system prompt from {SYSTEM_PROMPT_PATH}: {error}") from error
        if not self.system_prompt:
            raise AdmissionsAgentError(f"System prompt file is empty: {SYSTEM_PROMPT_PATH}")

    def run(
        self,
        question: str,
        trace_path: Path | None = None,
        status_callback: Callable[[str, str | None], None] | None = None,
    ) -> str:
        """Research a question and save a JSON trace of tools, evidence, and answer."""
        question = question.strip()
        if not question:
            raise AdmissionsAgentError("Please enter a research question.")

        research_tools = AdmissionsResearchTools()
        model = ChatOllama(model=self.model_name, base_url=self.base_url, temperature=0, request_timeout=300)
        graph = create_agent(model=model, tools=research_tools.tools, system_prompt=self.system_prompt)
        callbacks = [AgentStatusCallbackHandler(status_callback)] if status_callback else []
        try:
            result = graph.invoke(
                {"messages": [{"role": "user", "content": question}]},
                config={"recursion_limit": MAX_GRAPH_STEPS, "callbacks": callbacks},
            )
        except Exception as error:
            self._write_trace(question, "", research_tools, trace_path, error=str(error))
            raise AdmissionsAgentError(f"Admissions research failed: {error}") from error

        messages = result.get("messages", [])
        answer = str(messages[-1].content).strip() if messages else ""
        if not answer:
            raise AdmissionsAgentError("The agent returned an empty answer.")
        research_tools.trace.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "final_answer",
                "answer": answer,
            }
        )
        self._write_trace(question, answer, research_tools, trace_path)
        return answer

    @staticmethod
    def _write_trace(
        question: str,
        answer: str,
        research_tools: AdmissionsResearchTools,
        trace_path: Path | None,
        error: str | None = None,
    ) -> None:
        destination = trace_path or TRACE_DIR / f"admissions-{datetime.now(timezone.utc):%Y%m%dT%H%M%S%fZ}.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        trace: dict[str, Any] = {
            "question": question,
            "started_at": research_tools.trace[0]["timestamp"]
            if research_tools.trace
            else datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "search_count": research_tools.searches,
            "retrieval_count": research_tools.retrievals,
            "action_count": len(research_tools.trace),
            "actions": research_tools.trace,
            "evidence": research_tools.evidence,
            "answer": answer,
        }
        if error:
            trace["error"] = error
        destination.write_text(json.dumps(trace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research ASU undergraduate admissions using live web evidence.")
    parser.add_argument("question", nargs="?", help="Optional first question; omit to start an interactive session.")
    parser.add_argument("--trace", type=Path, help="Optional path for the first question's JSON trace.")
    args = parser.parse_args()

    try:
        agent = AdmissionsAgent()
    except AdmissionsAgentError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error

    question = args.question
    trace_path = args.trace
    print("ASU admissions research session. Enter /quit to end.\n")
    while True:
        if question is None:
            try:
                question = input("Researcher: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nSession ended.")
                break
        question = question.strip()
        if question.lower() == "/quit":
            print("Session ended.")
            break
        if not question:
            question = None
            continue

        try:
            answer = agent.run(question, trace_path=trace_path)
            print(f"\nAgent:\n{answer}\n")
        except AdmissionsAgentError as error:
            print(f"\nError: {error}\n", file=sys.stderr)
        question = None
        trace_path = None


if __name__ == "__main__":
    main()
