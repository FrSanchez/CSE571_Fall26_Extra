# fall_agent

A starter Ollama-backed agent for CSE 571 by **team awesome**. It accepts a question, can call an Open-Meteo weather tool, and returns a response from the model. This is a working starting point, not yet the complete evidence-seeking research system described in the course specification.

**Start with [CSE571_Fall26.md](CSE571_Fall26.md)** for the project scope, requirements, evaluation criteria, and deliverables.

- [PROJECT.md](docs/PROJECT.md) — Three-week plan, team responsibilities, and progress measures.
- [CONTRIBUTING.md](CONTRIBUTING.md) — Branch naming, pull requests, and required checks.
- [AGENTS.md](AGENTS.md) — Repository guidance for coding agents.
- [Architecture](docs/ARCHITECTURE.md) and [evaluation](docs/EVALUATION.md) — Placeholders pending team agreement.

## Setup and run

Use Python 3.11 or newer and a dedicated virtual environment. Install and start [Ollama](https://ollama.com/), then download a model supported by your machine. From the repository root on macOS/Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
ollama pull llama3.2
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama3.2
python -m agents.weather "What's the weather in Tempe, Arizona?"
```

If `OLLAMA_BASE_URL` is unset, the agent uses `http://localhost:11434`. `OLLAMA_MODEL` is required and must name a model available in Ollama. On Windows, activate with `.venv\Scripts\Activate.ps1` in PowerShell and set the variables in that shell. Omitting the question starts an interactive prompt:

```sh
python -m agents.weather
```

The weather tool uses the Open-Meteo geocoding and forecast APIs and does not require an API key. Python dependencies are configured in `pyproject.toml`.

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
