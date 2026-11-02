"""Example of instantiating and running the agent."""

from agent import Agent


def test_agent_returns_greeting() -> None:
    agent = Agent()

    assert agent.run() == "Hello, world!"
