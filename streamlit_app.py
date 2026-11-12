"""Basic Streamlit chat interface for the ASU admissions research agent."""

import json
import queue
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from agents.admissions import AdmissionsAgent, AdmissionsAgentError

KEEP_ALIVE = "24h"


def _warmup_ollama(agent: AdmissionsAgent) -> None:
    """Load the configured model and ask Ollama to keep it resident for 24 hours."""
    payload = json.dumps({
        "model": agent.model_name,
        "prompt": "",
        "stream": False,
        "keep_alive": KEEP_ALIVE,
    }).encode("utf-8")
    request = Request(
        f"{agent.base_url}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=300) as response:
            response.read()
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise AdmissionsAgentError(f"Ollama warmup failed with HTTP {error.code}: {detail}") from error
    except (TimeoutError, URLError) as error:
        raise AdmissionsAgentError(f"Could not warm up Ollama at {agent.base_url}: {error}") from error


def _run_with_status(
    agent: AdmissionsAgent,
    question: str,
    status_area: DeltaGenerator,
) -> str:
    """Run the agent in a worker thread while updating its live status in Streamlit."""
    events: queue.Queue[tuple[str, str | None]] = queue.Queue()
    result: queue.Queue[tuple[str, str]] = queue.Queue(maxsize=1)

    def report_status(event: str, value: str | None) -> None:
        events.put((event, value))

    def run_agent() -> None:
        try:
            result.put(("answer", agent.run(question, status_callback=report_status)))
        except AdmissionsAgentError as error:
            result.put(("error", str(error)))
        except Exception as error:  # Keep UI errors visible instead of losing the worker result.
            result.put(("error", str(error)))

    status_area.info("Starting research...")
    worker = threading.Thread(target=run_agent, daemon=True)
    worker.start()
    model_started_at: float | None = None
    last_elapsed_update = 0.0

    while worker.is_alive():
        try:
            event, value = events.get(timeout=0.25)
        except queue.Empty:
            if model_started_at is not None:
                elapsed = time.monotonic() - model_started_at
                if elapsed - last_elapsed_update >= 1:
                    status_area.info(f"Ollama is processing the prompt… {int(elapsed)}s elapsed")
                    last_elapsed_update = elapsed
            continue

        if event == "llm_start":
            model_started_at = time.monotonic()
            last_elapsed_update = 0.0
            status_area.info("Ollama is processing the prompt… 0s elapsed")
        elif event == "tool_start":
            model_started_at = None
            status_area.info(f"Running tool: {value or 'research tool'}")
        elif event == "tool_end":
            status_area.empty()

    worker.join()
    status_area.empty()
    result_kind, result_text = result.get()
    if result_kind == "error":
        return f"I couldn't complete that research run: {result_text}"
    return result_text


st.set_page_config(page_title="ASU Admissions Research", page_icon="🎓")
st.title("ASU Admissions Research")
st.caption("Ask an admissions research question. Each question starts a fresh evidence-gathering run.")

if "admissions_agent" not in st.session_state:
    try:
        st.session_state.admissions_agent = AdmissionsAgent()
    except AdmissionsAgentError as error:
        st.error(str(error))
        st.stop()

if "ollama_warmed" not in st.session_state:
    with st.spinner("Warming up Ollama (the model will stay loaded for 24 hours)…"):
        try:
            _warmup_ollama(st.session_state.admissions_agent)
            st.session_state.ollama_warmed = True
            st.success("Ollama is ready; the model will stay loaded for 24 hours.")
        except AdmissionsAgentError as error:
            st.session_state.ollama_warmed = False
            st.warning(f"Ollama warmup did not complete: {error}. The first question will retry model loading.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_ended" not in st.session_state:
    st.session_state.session_ended = False

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.session_ended:
    st.info("Research session ended.")
    if st.button("Start a new session"):
        st.session_state.messages = []
        st.session_state.session_ended = False
        st.rerun()

question = st.chat_input("Your question (enter /quit to end the session)", disabled=st.session_state.session_ended)
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    if question.strip().lower() == "/quit":
        st.session_state.messages.append({"role": "assistant", "content": "Research session ended."})
        st.session_state.session_ended = True
        st.rerun()

    with st.chat_message("assistant"):
        status_area = st.empty()
        answer = _run_with_status(st.session_state.admissions_agent, question, status_area)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
