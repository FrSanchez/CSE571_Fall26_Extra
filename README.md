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
- `src/agents/tools.py` — Weather retrieval and temperature-conversion tools.
- `tests/test_agent.py` and `tests/test_weather.py` — Agent and tool tests.
