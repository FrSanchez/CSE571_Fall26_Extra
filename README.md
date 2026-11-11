# fall_agent

A starter Ollama-backed agent for CSE 571 by **team awesome**. It accepts a question, can call an Open-Meteo weather tool, and returns a response from the model. This is a working starting point, not yet the complete evidence-seeking research system described in the course specification.

**Start with [CSE571_Fall26.md](CSE571_Fall26.md)** for the project scope, requirements, evaluation criteria, and deliverables.

- [PROJECT.md](docs/PROJECT.md) — Three-week plan, team responsibilities, and progress measures.
- [CONTRIBUTING.md](CONTRIBUTING.md) — Branch naming, pull requests, and required checks.
- [AGENTS.md](AGENTS.md) — Repository guidance for coding agents.
- [Architecture](docs/ARCHITECTURE.md) and [evaluation](docs/EVALUATION.md) — Placeholders pending team agreement.

## Setup and run

### Install and start Ollama 

1. Download and install Ollama from the [Ollama download page](https://ollama.com/download).
2. Start the Ollama service in a terminal:

   ```sh
   ollama serve
   ```

3. In another terminal, download the model:

   ```sh
   ollama pull qwen3.5:9b
   ```

The `qwen3.5:9b` model is the example used on a Mac mini with 16 GB of RAM; choose a model that fits your machine's available memory.

### Set up and run the agent

Use Python 3.11 or newer and a dedicated virtual environment. From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=qwen3.5:9b
python src/agents/weather.py "What's the weather in Tempe, Arizona?"
```

The first request may take longer or time out once or twice while Ollama loads the model. Try again after the model has loaded. If `OLLAMA_BASE_URL` is unset, the agent uses `http://localhost:11434`. `OLLAMA_MODEL` must name a model available in Ollama. On Windows, activate with `.venv\Scripts\Activate.ps1` in PowerShell and set the variables in that shell. Omitting the question starts an interactive prompt:

```sh
python src/agents/weather.py
```

The weather tool uses the Open-Meteo geocoding and forecast APIs and does not require an API key. Python dependencies are configured in `pyproject.toml`.

## DuckDuckGo and Jina Reader research agent

The research agent in `src/agents/first.py` uses DuckDuckGo for web results and Jina Reader to retrieve page content. DuckDuckGo does not require an API key; a Jina API key is optional:

```sh
export JINA_API_KEY=your_jina_api_key  # optional
python src/agents/first.py
```

`DuckDuckGoJinaSearchResults` is implemented in `src/agents/duckduckgo_jina_search.py` and can be imported directly by other agents:

```python
from agents.duckduckgo_jina_search import DuckDuckGoJinaSearchResults

search_tool = DuckDuckGoJinaSearchResults(max_results=5)
```

It returns JSON search-result records containing the title, URL, DuckDuckGo snippet, and Jina-extracted page text. If Jina cannot retrieve an individual result, that result includes a `reader_error` field.

## ASU admissions LangGraph agent

The project task suite now focuses on first-year undergraduate admissions at ASU, with UArizona as the comparison institution. See [the six questions](docs/ASU%20Transfer.md) and [the architecture](docs/ARCHITECTURE.md).

Start Ollama as described above, then run the admissions agent from the repository root (or an activated environment with the package installed):

```sh
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=qwen3.5:9b
python -m agents.admissions "How do ASU and UArizona first-year admission requirements compare?"
```

The agent uses DuckDuckGo search, Jina Reader page retrieval, structured claim evidence, and a LangGraph-backed tool loop. It returns a suggested next step after each answer, then accepts another question until you enter `/quit`. See [the interaction workflow](docs/AGENT_WORKFLOW.md). Each question writes a JSON trace to `runs/`; set `JINA_API_KEY` optionally for authenticated Jina access, or pass `--trace path/to/file.json` to choose a trace path for the first question. The trace includes retrieved page text. The available search and retrieval budgets are 8 searches and 12 pages per question.

For an installed package, invoke `python -m agents.admissions ...` with `src` on the Python path, as in the repository's configured pytest environment, or install the project with `python -m pip install -e ".[dev]"`.

### Streamlit web interface

Install the optional UI dependency and start the local web app:

```sh
python -m pip install -e ".[ui]"
streamlit run streamlit_app.py
```

The interface calls `AdmissionsAgent` from `src/agents/admissions.py`, displays the chat history, and supports `/quit` to end a session. While a tool runs, it shows the tool name; each new model response selects a message from the one-line-per-message `spinner.md` file. Click **Start a new session** to begin again. Each submitted question starts a fresh research run and saves its trace under `runs/`.

## Test, format, and compile/build

```sh
python -m pytest             # Run tests, including an Agent instance example
python -m tox               # Run isolated tests, lint, and formatting checks
python -m tox -e format     # Apply Ruff formatting
python -m build             # Build a wheel and source archive in dist/
```

Python needs no manual compilation to run; the build command creates installable distributions. Package metadata, dependencies, pytest, and tox are configured in `pyproject.toml`. Ruff settings are defined in `ruff.toml`.

GitHub Actions runs the tox `ruff` (lint and format checks) and `unit-tests` (tests with coverage) environments on pushes and pull requests. The workflow also supports manual runs.

## Layout

- `src/agents/agent.py` — Original Hello World agent scaffold.
- `src/agents/weather.py` — Ollama chat loop and CLI launcher.
- `src/agents/tools/` — Shared weather and admissions research tool package.
- `src/agents/admissions.py` — LangGraph admissions research agent.
- `streamlit_app.py` — Basic web chat interface for the admissions agent.
- `tests/test_agent.py` and `tests/test_weather.py` — Agent and tool tests.
