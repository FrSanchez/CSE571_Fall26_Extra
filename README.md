# fall_agent

An evidence-seeking web research agent for CSE 571 by **team awesome**. Currently a Python scaffold with a Hello World placeholder.

**Start with [CSE571_Fall26.md](CSE571_Fall26.md)** for the project scope, requirements, evaluation criteria, and deliverables.

- [PROJECT.md](PROJECT.md) — Three-week plan, team responsibilities, and progress measures.
- [AGENTS.md](AGENTS.md) — Contributor guidelines.

## Setup and run

Use Python 3.11 or newer and a dedicated virtual environment. From the repository root on macOS/Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python agent.py
```

On Windows, activate with `.venv\Scripts\Activate.ps1` in PowerShell. Installation includes PyTorch (`torch`) and scikit-learn; development tools include pytest, tox, Ruff, and build.

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

- `agent.py` — Placeholder `Agent` class and launcher; prints `Hello, world!`.
- `src/` — Reserved for future source code; currently empty.
- `tests/test_agent.py` — Example of constructing and running the agent.
