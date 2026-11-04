"""Tests for weather tools and temperature conversions."""

import io
import json
from urllib.request import Request

import pytest

import agents.tools as tools
import agents.weather as weather
from agents.tools import celsius2farenheit, farenheit2celsius
from agents.weather import Agent


def json_response(data: dict[str, object]) -> io.BytesIO:
    return io.BytesIO(json.dumps(data).encode("utf-8"))


@pytest.mark.parametrize(
    ("celsius", "expected_farenheit"),
    [(0.0, 32.0), (100.0, 212.0), (27.0, 80.6)],
)
def test_celsius2farenheit(celsius: float, expected_farenheit: float) -> None:
    assert celsius2farenheit(celsius) == pytest.approx(expected_farenheit)


@pytest.mark.parametrize(
    ("farenheit", "expected_celsius"),
    [(32.0, 0.0), (212.0, 100.0), (80.6, 27.0)],
)
def test_farenheit2celsius(farenheit: float, expected_celsius: float) -> None:
    assert farenheit2celsius(farenheit) == pytest.approx(expected_celsius)


def test_agent_advertises_and_uses_weather_and_temperature_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")
    chat_responses = [
        {
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [{"function": {"name": "get_weather", "arguments": {"location": "Tempe, Arizona"}}}],
            }
        },
        {
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [{"function": {"name": "celsius2farenheit", "arguments": {"temperature": 27}}}],
            }
        },
        {"message": {"role": "assistant", "content": "It is currently 80.6°F in Tempe."}},
    ]
    chat_payloads: list[dict[str, object]] = []

    def fake_urlopen(request: Request, timeout: int) -> io.BytesIO:
        if request.full_url.endswith("/api/chat"):
            payload = json.loads(request.data.decode("utf-8"))
            chat_payloads.append(payload)
            return json_response(chat_responses.pop(0))
        if "geocoding-api.open-meteo.com" in request.full_url:
            return json_response(
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
                }
            )
        return json_response(
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
            }
        )

    monkeypatch.setattr(tools, "urlopen", fake_urlopen)
    monkeypatch.setattr(weather, "urlopen", fake_urlopen)

    answer = Agent().run("What's the weather in Tempe, Arizona?")

    assert answer == "It is currently 80.6°F in Tempe."
    assert [tool["function"]["name"] for tool in chat_payloads[0]["tools"]] == [
        "get_weather",
        "celsius2farenheit",
        "farenheit2celsius",
    ]
    assert "Fahrenheit by default" in chat_payloads[0]["messages"][0]["content"]
    assert chat_payloads[1]["messages"][-1]["tool_name"] == "get_weather"
    assert chat_payloads[2]["messages"][-1]["tool_name"] == "celsius2farenheit"
    assert json.loads(chat_payloads[2]["messages"][-1]["content"]) == pytest.approx(80.6)
