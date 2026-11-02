# Repository Guidelines

## Project Scope & Structure

`fall_agent` (author: **team awesome**) is a CSE 571 evidence-seeking web research agent, currently a Hello World scaffold.

- [CSE571_Fall26.md](CSE571_Fall26.md) is the authoritative specification; preserve the original PDF at the root.
- [PROJECT.md](docs/PROJECT.md) defines the three-week, four-person plan, technical ownership, and progress measures.
- [README.md](README.md) provides setup and usage instructions; keep it concise.
- `agent.py` contains the installable top-level `Agent` class and `main()` launcher.
- `src/` is intentionally empty. Do not recreate `src/fall_agent/` without an agreed layout change.
- `tests/test_agent.py` instantiates `Agent` using `from agent import Agent`.

Future implementation must follow the specification: six questions in one bounded domain, adaptive research, retrieved-page evidence, claim verification, citations, budgets, traces, and baseline comparison. These capabilities are not implemented yet.

## Configuration & Dependencies

Use Python 3.11+. `pyproject.toml` centralizes setuptools packaging, metadata, runtime dependencies, dev extras, pytest, and tox. Keep this configuration consolidated; no `tox.ini` or requirements files are needed.

Runtime dependencies are `torch` and `scikit-learn`. Dev extras include build, pytest, pytest-cov, Ruff, and tox >=4.21.2. Ruff settings remain in `ruff.toml`.

## Setup, Run & Build

Use a dedicated virtual environment from the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python agent.py                 # Print Hello, world!
python -m pytest               # Run tests
python -m tox                  # Run py, ruff, and unit-tests
python -m tox -e unit-tests     # Tests with agent coverage
python -m tox -e format         # Apply Ruff formatting
python -m build                # Wheel and source archive in dist/
```

Windows PowerShell activation: `.venv\Scripts\Activate.ps1`. Python requires no manual compilation before running.

## Coding Style & Testing

Use four-space indentation, type annotations, `snake_case` functions/files, and `PascalCase` classes. Ruff configures 120-character lines and E, F, ANN rules; preserve its existing exclusions. The tox Ruff environment checks lint and formatting.

Use pytest with `tests/test_*.py` files and `test_*` functions. Coverage targets `agent`, not empty `src/`, and produces terminal, HTML, and XML reports. No coverage threshold is configured.

## Agent Workflow & Contribution Rules

Ask whether the user wants you to run checks or will run them themselves before executing tests, tox, formatting, builds, dependency installation, or the application. Avoid colliding with their active processes. Report checks actually performed and those left unrun.

Recent commits use concise, imperative subjects such as `Add pyproject and test config`. PRs should explain purpose, affected components, validation, and relevant issues. Keep generated environments, caches, build artifacts, and coverage output out of commits.
