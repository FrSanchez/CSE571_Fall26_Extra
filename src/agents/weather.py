"""A small Ollama-backed agent with a live weather tool."""

import argparse
import json
import logging
import os
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

if __package__:
    from .tools import (
        TOOLS,
        AgentError,
        celsius2farenheit,
        farenheit2celsius,
        get_weather,
    )
else:
    from tools import TOOLS, AgentError, celsius2farenheit, farenheit2celsius, get_weather


# Configure the logger
logging.basicConfig(
    level=logging.DEBUG,  # Minimum level to capture
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log message format
    filename="weather.log",  # Optional: write logs to a file
    filemode="w",  # 'w' to overwrite file each run, 'a' to append
)

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen3.5:9b"
OLLAMA_REQUEST_TIMEOUT = 300
MAX_TOOL_TURNS = 9


class Agent:
    """A small tool-using chat agent connected to a local Ollama server."""

    def __init__(self) -> None:
        self.base_url = os.environ.get("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).rstrip("/")
        self.model = os.environ.get("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL).strip()
        if not self.model:
            raise AgentError("Set OLLAMA_MODEL to the name of a model available in Ollama.")
        if not self.base_url:
            raise AgentError("OLLAMA_BASE_URL must be a non-empty URL.")

    def run(self, question: str) -> str:
        """Answer a question, allowing Ollama to call the weather tool."""
        question = question.strip()
        if not question:
            raise AgentError("Please enter a question.")

        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. Use the get_weather tool when a question asks about "
                    "current weather. Do not invent weather data; explain tool errors clearly. "
                    "Weather temperatures are returned in Celsius. Report temperatures in Fahrenheit "
                    "by default: call celsius2farenheit for each temperature you report unless the "
                    "user explicitly asks for Celsius. If Celsius is requested, report the weather "
                    "tool's Celsius values without converting. Use the conversion tools for explicit "
                    "temperature-conversion requests, and do not do the arithmetic yourself."
                ),
            },
            {"role": "user", "content": question},
        ]

        for _ in range(MAX_TOOL_TURNS):
            logging.debug("Sending messages to Ollama: %s", messages)
            response = self._chat(messages)
            message = response.get("message")
            if not isinstance(message, dict):
                raise AgentError("Ollama returned a response without a message.")

            logging.debug("Received message from Ollama: %s", message)
            tool_calls = message.get("tool_calls", [])
            logging.debug("Received tool calls from Ollama: %s", tool_calls)
            if not tool_calls:
                logging.debug("Ollama returned a final answer.")
                content = message.get("content")
                if not isinstance(content, str) or not content.strip():
                    raise AgentError("Ollama returned an empty answer.")
                return content.strip()

            messages.append(message)
            for tool_call in tool_calls:
                logging.debug("Executing tool call from Ollama: %s", tool_call)
                tool_name, result = self._execute_tool(tool_call)
                messages.append({"role": "tool", "tool_name": tool_name, "content": json.dumps(result)})

        raise AgentError(f"Ollama exceeded the limit of {MAX_TOOL_TURNS} tool turns.")

    def _chat(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": TOOLS,
            "stream": False,
        }
        request = Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=OLLAMA_REQUEST_TIMEOUT) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            detail = error.read(1024).decode("utf-8", errors="replace").strip()
            try:
                error_data = json.loads(detail)
            except json.JSONDecodeError:
                error_data = None
            if isinstance(error_data, dict) and isinstance(error_data.get("error"), str):
                detail = error_data["error"]
            suffix = f": {detail}" if detail else ""
            raise AgentError(f"Ollama request failed with HTTP {error.code}{suffix}.") from error
        except (URLError, TimeoutError, OSError) as error:
            raise AgentError(f"Could not connect to Ollama at {self.base_url}: {error}.") from error
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise AgentError("Ollama returned invalid JSON.") from error
        if not isinstance(data, dict):
            raise AgentError("Ollama returned an unexpected response.")
        return data

    @staticmethod
    def _execute_tool(tool_call: object) -> tuple[str, dict[str, Any] | float]:
        if not isinstance(tool_call, dict):
            raise AgentError("Ollama returned an invalid tool call.")
        function = tool_call.get("function")
        if not isinstance(function, dict):
            raise AgentError("Ollama returned an invalid tool call.")
        name = function.get("name")
        if not isinstance(name, str):
            raise AgentError("Ollama returned a tool call without a valid name.")
        arguments = function.get("arguments")
        if not isinstance(arguments, dict):
            raise AgentError(f"Ollama provided invalid arguments for {name}.")

        if name == "get_weather":
            location = arguments.get("location")
            if not isinstance(location, str):
                raise AgentError("Ollama provided invalid arguments for get_weather.")
            return name, get_weather(location)

        if name in {"celsius2farenheit", "farenheit2celsius"}:
            temperature = arguments.get("temperature")
            if isinstance(temperature, bool) or not isinstance(temperature, (int, float)):
                raise AgentError(f"Ollama provided invalid arguments for {name}.")
            conversion = celsius2farenheit if name == "celsius2farenheit" else farenheit2celsius
            return name, conversion(float(temperature))

        raise AgentError("Ollama requested an unsupported tool.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat with the Ollama weather-tool agent.")
    parser.add_argument("question", nargs="?", help="Question to ask; omit to enter one interactively.")
    args = parser.parse_args()
    question = args.question or input("You: ")
    try:
        print(Agent().run(question))
    except AgentError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
