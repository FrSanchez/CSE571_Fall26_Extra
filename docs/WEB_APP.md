# Streamlit Web App

## Purpose

The Streamlit interface makes the admissions research agent easier to demonstrate and explore. It is a lightweight project UI, not a finished application or a production deployment.

## Architecture

`streamlit_app.py` provides a basic chat interface and calls `AdmissionsAgent` from `src/agents/admissions.py`. The agent runs a LangGraph research cycle with local Ollama and the web search, page retrieval, and evidence tools. Each submitted question gets a fresh research run; the visible chat history is for reference and is not passed into the next run as conversation context. Each run writes its trace under `runs/`.

When a Streamlit session starts, the app sends Ollama an empty-prompt warmup request with `keep_alive` set to `24h`. Research model calls use the same setting, keeping the model loaded between requests. If warmup fails, the app shows a warning and still allows questions to be submitted.

The UI displays the active tool name while a tool is running. When a model call starts, it shows an elapsed timer for Ollama's prompt processing and response generation. Ollama's `processed`/`total` prompt-processing log lines are emitted by the Ollama server and are not exposed as incremental progress by the API, so the UI cannot show an exact percentage or token count.

## Run locally

Install the optional UI dependency from the repository root:

```sh
python -m pip install -e ".[ui]"
```

Start Ollama in another terminal, then launch the interface:

```sh
streamlit run streamlit_app.py --logger.level=info
```

Set `OLLAMA_BASE_URL` and `OLLAMA_MODEL` if you need values other than the defaults documented in the [README](../README.md). Enter `/quit` in the chat to end the session; select **Start a new session** to clear the displayed conversation and continue.

The `--logger.level=info` option is a Streamlit CLI configuration flag. It belongs after the app filename without a `--` separator; arguments after that separator are passed to the app script. See the [Streamlit run CLI reference](https://docs.streamlit.io/develop/api-reference/cli/run).

## Scope and limitations

The interface is intended for classroom demonstrations and development. It has a simple chat layout and minimal session handling. It does not provide production-grade authentication, persistent conversation storage, deployment configuration, or operational monitoring.
