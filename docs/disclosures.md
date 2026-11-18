# Project Disclosures

## Models, versions, and framework

- **Language/runtime:** Python 3.12 was used for development and execution. The package metadata currently permits Python 3.11 and newer.
- **Language model:** The admissions agent uses `qwen3:8b` through Ollama by default (`OLLAMA_MODEL` can override this). The repository does not record an Ollama server version or an immutable model digest; record the exact Ollama and model versions used for evaluated runs here.
- **Frameworks:** LangChain (`langchain` and `langchain-ollama`) and LangGraph provide the model integration, tool interface, and agent loop. The admissions agent is a single-agent system.
- **Version pinning:** Runtime dependency versions are not pinned in `pyproject.toml`; it specifies package names without version constraints.

## API

- **Ollama:** Model requests are sent to a locally running Ollama service, defaulting to `http://localhost:11434`. No hosted LLM API is configured by default.
- **Jina Reader:** Retrieved webpages are read through `https://r.jina.ai/`. `JINA_API_KEY` is optional and, when set, is sent to Jina Reader for authenticated access.
- **DuckDuckGo:** The `ddgs` package is used for live web search. The project does not configure a separate DuckDuckGo API key.
- **Open-Meteo:** The repository's weather tools call the Open-Meteo geocoding and forecast APIs. These support the separate weather agent and are not part of the admissions research loop.

## External Data

The admissions agent searches the live web using DuckDuckGo and retrieves selected webpages through Jina Reader. Search results include titles, URLs, snippets, and ranks; the agent is instructed to use retrieved page text, rather than snippets, as evidence. Retrieved content, evidence records, search results, and answers are saved in per-run JSON traces under `runs/` by default. Because web results and pages can change over time, traces represent the sources available during each run.

For admissions questions, the prompt prioritizes official ASU and University of Arizona sources and credible institutional datasets where appropriate. The weather agent uses Open-Meteo data. No separately curated external dataset is included in the repository.

## Prompt

The admissions agent's system prompt is maintained in [`src/agents/system_prompt.md`](../src/agents/system_prompt.md). It defines the first-year ASU admissions scope (with UArizona comparisons), research and retrieval procedure, evidence and citation requirements, uncertainty and abstention behavior, and search/retrieval limits. It is provided to the model at runtime. The weather agent uses a prompt defined in its source code.

## Generative AI assistance

The project includes a generative-AI agent powered by Ollama and Qwen for web research, evidence organization, and answer drafting. Generative-AI tools may also have assisted development of the code, documentation, testing, or debugging; the specific tools, versions, and tasks used during development have not been documented in the repository. **Complete this disclosure with the team's actual development-use details before submission**, including any AI assistant/model used, what it helped produce or revise, and what team members reviewed or verified.
