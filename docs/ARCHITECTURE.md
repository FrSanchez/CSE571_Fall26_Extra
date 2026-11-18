# ASU admissions research agent architecture

## Goal and domain

The agent researches first-year undergraduate admission questions for Arizona State University (ASU), with the University of Arizona as the comparison institution. The six-question suite is in [ASU Transfer.md](./ASU%20Transfer.md); the filename is retained for continuity, though its scope now covers undergraduate admissions rather than transfer equivalencies.

## Initial architecture

The first implementation is a single LangGraph agent, invoked through LangChain's graph-backed `create_agent` API, with a local Ollama model selecting actions. Its editable system prompt lives in `src/agents/system_prompt.md` and is loaded when `AdmissionsAgent` is initialized. Setuptools includes the prompt in built packages. The agent loops over the user question, search results, retrieved page text, evidence records, and prior tool results. This is the required initial route; separate research/verification/synthesis agents remain an optional later experiment and would need a baseline comparison.

```text
Question -> Ollama-backed LangGraph agent -> web_search
                 ^                              |
                 |                              v
                 +-- tool results <- fetch_page
                 |                    |
                 +-- evidence <- save_evidence / list_evidence
                 |
                 +-- cited answer or abstention
```

## Tools and evidence

`src/agents/tools/` is the shared tool package. Its `__init__.py` preserves the existing weather tools and exports the admissions research tool factory. Each admissions run creates its own four tools:

- `web_search(query)` uses DuckDuckGo and returns ranked titles, URLs, snippets, and ranks. Snippets guide retrieval but are not evidence.
- `fetch_page(url)` retrieves readable page content through Jina Reader. It stores title, URL, retrieval timestamp, content, and available metadata for the run.
- `save_evidence(...)` stores a claim, source, exact passage, source-quality assessment, verification label, and rationale. It accepts only successfully retrieved pages and quotations found verbatim in their text.
- `list_evidence()` returns the structured records for review before answering.

Searches are limited to 8 and page retrievals to 12 per question. Each tool action, search result, retrieved page, evidence item, and final answer is written to a JSON trace under `runs/` by default; pass `--trace` to select a path. Trace files may contain retrieved page text and should be reviewed before sharing.

The initial verification label is assigned by the model after it inspects the quote and source context. Quote membership and retrieved-source provenance are checked by the tool; semantic verification still requires evaluation. Sources should prioritize official ASU and UArizona pages, with credible institutional datasets for published admission statistics. The system prompt directs the agent to identify the term, population, and date associated with requirements, deadlines, and statistics, and to abstain on student-specific outcomes that public sources cannot establish.

## Runtime

Set `OLLAMA_BASE_URL` (default `http://localhost:11434`) and `OLLAMA_MODEL` (default `qwen3.5:9b`), start Ollama, then run:

```sh
python -m agents.admissions "What are ASU's current first-year admission requirements?"
```

The agent uses live DuckDuckGo search and Jina Reader retrieval; `JINA_API_KEY` is optional. Search availability and page contents may vary over time, so the JSON trace is part of each evaluated run.

## Next implementation milestones

1. Evaluate the six-question suite and inspect traces for coverage, citation validity, and sensible abstentions.
2. Add deterministic validation and explicit freshness/source-quality checks based on observed failures.
3. Implement a fixed-query or search-and-summarize baseline and compare answer correctness, citations, adaptivity, and tool cost.
4. Consider specialized agents only if the single-agent evaluation shows a concrete benefit to test.
