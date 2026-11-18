# Repository Guidelines

## Project Scope & Structure

`fall_agent` (author: **team awesome**) is a CSE 571 evidence-seeking web research agent. The current task domain is ASU first-year undergraduate admissions, compared with the University of Arizona.

- [CSE571_Fall26.md](CSE571_Fall26.md) is the authoritative specification; preserve the original PDF at the root.
- [PROJECT.md](docs/PROJECT.md) defines the three-week, four-person plan, technical ownership, and progress measures.
- [README.md](README.md) provides setup and usage instructions; keep it concise.
- `src/agents/agent.py` contains the original Hello World scaffold.
- `src/agents/admissions.py` runs the LangGraph admissions research agent with local Ollama.
- `src/agents/system_prompt.md` contains the admissions agent's runtime system prompt.
- `src/agents/weather.py` contains the Ollama-backed weather agent and `main()` launcher.
- `src/agents/tools/__init__.py` exports weather and admissions research tools.
- `src/agents/tools/research.py` implements web search, page retrieval, evidence storage, and per-run traces.
- `tests/test_agent.py` and `tests/test_weather.py` import from `agents.weather`.

The agent implementation must follow the specification: six questions in one bounded domain, adaptive research, retrieved-page evidence, claim verification, citations, budgets, traces, and baseline comparison. The initial agent/tools scaffold is implemented; evaluation and a baseline comparison remain future work.

## Required Project Reports & Evaluation Artifacts

Use the deliverables in [CSE571_Fall26.md](CSE571_Fall26.md), section 13, as the source of truth. The project requires:

- **One-page preliminary rational-agent report (20/100):** performance measure, prior knowledge, available actions, percept sequence, and a justified classification of all six environment properties (observability, number of agents, determinism, episodic/sequential, static/dynamic, discrete/continuous). See section 12.
- **Three-page technical report (25/100):** architecture; model/runtime; tools and their limitations; prompts or decision policies; evidence-memory representation; claim-verification process; stopping policy and budgets; baseline design; and limitations.
- **Six-question results table (30/100):** for each required task category/question, include the final answer, outcome (answered/disputed/abstained), search count, retrieved-page count, model/tool-call count, cited-source count, and verification results. Freeze the same six questions before final evaluation.
- **Representative complete traces (10/100):** include successful, unsuccessful, conflicting-evidence, and insufficient-evidence cases. Traces should expose timestamps, queries/results, retrieved URLs and text, evidence records, verification, citations, and final answers.
- **At least two qualitative case studies (10/100):** at least one must explain an adaptive search or verification decision that materially affected the final answer.
- **Development disclosure (5/100):** all model names/versions, frameworks, APIs, external data, prompts, tools, and generative-AI assistance used.
- **Conditional multi-agent comparison:** only if using multiple agents, compare against a simpler single-agent or ablated system and analyze whether specialization improved results.

The deliverables above are separate report/evaluation artifacts; the specification does not prescribe a separate report for each item. Package the table, traces, case studies, and disclosure with the reports or as clearly labeled appendices/artifacts. Also submit source code in a private Git repository or ZIP archive. Evaluation should document baseline comparison, and the technical report should describe the baseline; a multi-agent comparison is additionally required only for a multi-agent implementation.

## Configuration & Dependencies

Use Python 3.11+. `pyproject.toml` centralizes setuptools packaging, metadata, runtime dependencies, dev extras, pytest, and tox. Keep this configuration consolidated; no `tox.ini` or requirements files are needed.

Runtime dependencies include LangGraph, LangChain Ollama, DuckDuckGo search, `torch`, and `scikit-learn`. Dev extras include build, pytest, pytest-cov, Ruff, and tox >=4.21.2. Ruff settings remain in `ruff.toml`.

## Setup, Run & Build

Use a dedicated virtual environment from the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m agents.weather        # Start the weather-agent prompt (after package install)
python -m pytest               # Run tests
python -m tox                  # Run py, ruff, and unit-tests
python -m tox -e unit-tests     # Tests with agent coverage
python -m tox -e format         # Apply Ruff formatting
python -m build                # Wheel and source archive in dist/
```

Windows PowerShell activation: `.venv\Scripts\Activate.ps1`. Python requires no manual compilation before running.

## Coding Style & Testing

Use four-space indentation, type annotations, `snake_case` functions/files, and `PascalCase` classes. Ruff configures 120-character lines and E, F, ANN rules; preserve its existing exclusions. The tox Ruff environment checks lint and formatting.

Use pytest with `tests/test_*.py` files and `test_*` functions. Coverage targets `agents.weather`, `agents.admissions`, and `agents.tools.research`, producing terminal, HTML, and XML reports. No coverage threshold is configured.

## Agent Workflow & Contribution Rules

Ask whether the user wants you to run checks or will run them themselves before executing tests, tox, formatting, builds, dependency installation, or the application. Avoid colliding with their active processes. Report checks actually performed and those left unrun.

Recent commits use concise, imperative subjects such as `Add pyproject and test config`. PRs should explain purpose, affected components, validation, and relevant issues. Keep generated environments, caches, build artifacts, and coverage output out of commits.
