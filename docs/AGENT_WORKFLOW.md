# Admissions agent interaction workflow

The admissions agent runs as an interactive research session. A researcher can ask multiple questions in the same process; the process ends only when the researcher enters `/quit` as a standalone command (or closes the input stream).

## Conversation cycle

For each question, the agent:

1. Starts a fresh LangGraph research run with a new evidence store and tool budget.
2. Searches the live web, retrieves selected pages, records claim-level evidence, and adapts its searches as needed.
3. Returns a concise answer with citations, uncertainty or abstention where appropriate, and a **Suggested next step** for the person doing the research.
4. Prompts for the next question and repeats the cycle.

The run state is isolated per question: search and retrieval budgets and evidence from one question do not carry into the next question. The loaded system prompt is reused by the interactive process, while each question gets its own research tools and graph invocation. The local Ollama service remains running between questions. Each question writes its own JSON trace under `runs/`; an optional `--trace` path applies to the first question only, with later questions using generated trace filenames.

## Starting and ending a session

The session is available from either the command line or the basic Streamlit chat page. Install the UI extra and start the page with:

```sh
python -m pip install -e ".[ui]"
streamlit run streamlit_app.py
```

In the web interface, enter questions in the chat box. Enter `/quit` to end the session; use **Start a new session** to clear the visible conversation and resume. The displayed history is for reference; each submitted question starts a separate research run with a fresh evidence store and budget.

While research is running, the UI displays the name of an active tool (such as `web_search` or `fetch_page`). Each time the model starts a response, the UI selects a message from the root-level `spinner.md` list. A tool-start event replaces that message with the active tool name, and the next model call selects another message. Keep one complete status message on each line in that file.

Start an interactive session:

```sh
python -m agents.admissions
```

An optional question can be supplied to start the session immediately:

```sh
python -m agents.admissions "What are ASU's current first-year admission requirements?"
```

After each answer, enter another research question. Enter `/quit` to end the session. Blank inputs are ignored, and a research error is reported without ending the session.

## Response format

Each response answers the submitted question using sources retrieved during that question's run. It should cite supported claims, explain conflicting or insufficient evidence, and finish with a practical next step such as checking a current official page, clarifying the relevant application term, or comparing an equivalent requirement at UArizona. The suggestion is guidance for the researcher and does not automatically launch another run; the researcher decides what to ask next.
