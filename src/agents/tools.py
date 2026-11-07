"""Weather retrieval and temperature-conversion tools."""

import json
import logging
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DEFAULT_REQUEST_TIMEOUT = 30

WEATHER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city or place name.",
        "parameters": {
            "type": "object",
            "properties": {"location": {"type": "string", "description": "City or place name"}},
            "required": ["location"],
        },
    },
}

CELSIUS2FARENHEIT_TOOL = {
    "type": "function",
    "function": {
        "name": "celsius2farenheit",
        "description": "Convert a temperature from Celsius to Fahrenheit.",
        "parameters": {
            "type": "object",
            "properties": {"temperature": {"type": "number", "description": "Temperature in Celsius"}},
            "required": ["temperature"],
        },
    },
}

FARENHEIT2CELSIUS_TOOL = {
    "type": "function",
    "function": {
        "name": "farenheit2celsius",
        "description": "Convert a temperature from Fahrenheit to Celsius.",
        "parameters": {
            "type": "object",
            "properties": {"temperature": {"type": "number", "description": "Temperature in Fahrenheit"}},
            "required": ["temperature"],
        },
    },
}

TOOLS = [WEATHER_TOOL, CELSIUS2FARENHEIT_TOOL, FARENHEIT2CELSIUS_TOOL]

WEATHER_CODES = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    56: "light freezing drizzle",
    57: "dense freezing drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    66: "light freezing rain",
    67: "heavy freezing rain",
    71: "slight snow fall",
    73: "moderate snow fall",
    75: "heavy snow fall",
    77: "snow grains",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    85: "slight snow showers",
    86: "heavy snow showers",
    95: "thunderstorm",
    96: "thunderstorm with slight hail",
    99: "thunderstorm with heavy hail",
}


class AgentError(Exception):
    """Raised when agent configuration or a tool interaction fails."""


def celsius2farenheit(temperature: float) -> float:
    """Convert Celsius to Fahrenheit using F = C * 9/5 + 32."""
    logging.debug("Converting Celsius to Fahrenheit: %s°C", temperature)
    return temperature * 9 / 5 + 32


def farenheit2celsius(temperature: float) -> float:
    """Convert Fahrenheit to Celsius using C = (F - 32) * 5/9."""
    logging.debug("Converting Fahrenheit to Celsius: %s°F", temperature)
    return (temperature - 32) * 5 / 9


def _get_json(url: str, purpose: str) -> dict[str, Any]:
    request = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=DEFAULT_REQUEST_TIMEOUT) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise AgentError(f"{purpose} failed with HTTP {error.code}.") from error
    except (URLError, TimeoutError, OSError) as error:
        raise AgentError(f"{purpose} failed: {error}.") from error
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AgentError(f"{purpose} returned invalid JSON.") from error
    if not isinstance(data, dict):
        raise AgentError(f"{purpose} returned an unexpected response.")
    return data


def get_weather(location: str) -> dict[str, Any]:
    """Look up a place and return its current weather using Open-Meteo."""
    location = location.strip()
    logging.debug("Looking up weather for location: %s", location)
    if not location:
        raise AgentError("The weather tool requires a non-empty location.")

    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search?" + urlencode(
        {"name": location, "count": 1, "language": "en", "format": "json"}
    )
    geocoding = _get_json(geocoding_url, "Weather location lookup")
    results = geocoding.get("results")
    logging.debug("Called geocoding API, received results: %s", results)
    if not isinstance(results, list) or not results:
        raise AgentError(f"No location found for {location!r}.")

    place = results[0]
    logging.debug("Using first geocoding result: %s", place)
    if not isinstance(place, dict) or "latitude" not in place or "longitude" not in place:
        raise AgentError("Weather location lookup returned incomplete coordinates.")

    forecast_url = "https://api.open-meteo.com/v1/forecast?" + urlencode(
        {
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "timezone": "auto",
        }
    )
    forecast = _get_json(forecast_url, "Current weather lookup")
    current = forecast.get("current")
    logging.debug("Called weather API, received current weather: %s", current)
    if not isinstance(current, dict) or "weather_code" not in current:
        raise AgentError("Current weather lookup returned incomplete weather data.")

    code = current["weather_code"]
    current["conditions"] = WEATHER_CODES.get(code, f"unknown conditions (code {code})")
    weather = {
        "location": {
            "name": place.get("name", location),
            "admin1": place.get("admin1"),
            "country": place.get("country"),
            "timezone": forecast.get("timezone"),
        },
        "current": current,
        "units": forecast.get("current_units", {}),
    }
    logging.debug("Returning weather data: %s", weather)
    return weather
