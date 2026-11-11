"""Tests for the Ollama agent and its weather tool."""

import io
import json
from urllib.error import HTTPError
from urllib.request import Request

import pytest

import agents.tools as tools
import agents.weather as agent
from agents.weather import Agent, AgentError
from agents.tools import get_weather


def json_response(data: dict[str, object]) -> io.BytesIO:
    return io.BytesIO(json.dumps(data).encode("utf-8"))


def test_agent_uses_weather_tool_and_returns_ollama_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")
    responses = [
        {
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [{"function": {"name": "get_weather", "arguments": {"location": "Tempe, Arizona"}}}],
            }
        },
        {
            "results": [
                {
                    "name": "Tempe",
                    "admin1": "Arizona",
                    "country": "United States",
                    "latitude": 33.4,
                    "longitude": -111.9,
                }
            ]
        },
        {
            "timezone": "America/Phoenix",
            "current": {
                "temperature_2m": 27.0,
                "relative_humidity_2m": 22,
                "apparent_temperature": 26.0,
                "weather_code": 0,
                "wind_speed_10m": 8.0,
            },
            "current_units": {"temperature_2m": "°C"},
        },
        {
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [{"function": {"name": "celsius2farenheit", "arguments": {"temperature": 27.0}}}],
            }
        },
        {"message": {"role": "assistant", "content": "It is currently 80.6°F and clear in Tempe."}},
    ]
    requested_urls: list[str] = []

    def fake_urlopen(request: Request, timeout: int) -> io.BytesIO:
        requested_urls.append(request.full_url)
        return json_response(responses.pop(0))

    monkeypatch.setattr(agent, "urlopen", fake_urlopen)
    monkeypatch.setattr(tools, "urlopen", fake_urlopen)

    answer = Agent().run("What's the weather in Tempe, Arizona?")

    assert answer == "It is currently 80.6°F and clear in Tempe."
    assert len(requested_urls) == 5
    assert requested_urls[0] == "http://localhost:11434/api/chat"
    assert "geocoding-api.open-meteo.com" in requested_urls[1]
    assert "api.open-meteo.com/v1/forecast" in requested_urls[2]
    assert requested_urls[3:] == [
        "http://localhost:11434/api/chat",
        "http://localhost:11434/api/chat",
    ]


def test_agent_uses_default_model_when_not_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)

    assert Agent().model == agent.DEFAULT_OLLAMA_MODEL


def test_get_weather_rejects_unknown_location(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tools, "urlopen", lambda request, timeout: json_response({"results": []}))

    with pytest.raises(AgentError, match="No location found"):
        get_weather("Unknown place")


def test_agent_rejects_unsupported_tool(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")

    with pytest.raises(AgentError, match="unsupported tool"):
        Agent._execute_tool({"function": {"name": "unknown", "arguments": {}}})


def test_agent_reports_ollama_http_error_detail(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_MODEL", "missing-model")
    error_body = io.BytesIO(b'{"error":"model not found"}')

    def raise_http_error(request: Request, timeout: int) -> io.BytesIO:
        raise HTTPError(request.full_url, 404, "Not Found", None, error_body)

    monkeypatch.setattr(agent, "urlopen", raise_http_error)

    with pytest.raises(AgentError, match="HTTP 404: model not found"):
        Agent().run("What's the weather?")
