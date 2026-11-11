"""Basic Streamlit chat interface for the ASU admissions research agent."""

import queue
import random
from pathlib import Path
import threading

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from agents.admissions import AdmissionsAgent, AdmissionsAgentError

SPINNER_FILE = Path(__file__).with_name("spinner.md")


def _load_spinner_messages() -> list[str]:
    """Read the one-message-per-line list used for model-call status updates."""
    try:
        messages = [line.strip() for line in SPINNER_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    except OSError:
        messages = []
    return messages or ["Searching sources and checking evidence..."]


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

    messages = _load_spinner_messages()
    last_message: str | None = None

    def next_message() -> str:
        nonlocal last_message
        choices = [message for message in messages if message != last_message] or messages
        last_message = random.choice(choices)
        return last_message

    status_area.info("Starting research...")
    worker = threading.Thread(target=run_agent, daemon=True)
    worker.start()

    while worker.is_alive():
        try:
            event, value = events.get(timeout=0.1)
        except queue.Empty:
            continue

        if event == "llm_start":
            status_area.info(next_message())
        elif event == "tool_start":
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
