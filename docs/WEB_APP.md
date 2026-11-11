# Streamlit Web App

## Purpose

The Streamlit interface makes the admissions research agent easier to demonstrate and explore. It is a lightweight project UI, not a finished application or a production deployment.

## Architecture

`streamlit_app.py` provides a basic chat interface and calls `AdmissionsAgent` from `src/agents/admissions.py`. The agent runs a LangGraph research cycle with local Ollama and the web search, page retrieval, and evidence tools. Each submitted question gets a fresh research run; the visible chat history is for reference and is not passed into the next run as conversation context. Each run writes its trace under `runs/`.

The UI displays the active tool name while a tool is running. When the model starts a response, it selects a wait message from the root-level `spinner.md` file. This file contains one message per line and can be edited to change the status messages.

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
