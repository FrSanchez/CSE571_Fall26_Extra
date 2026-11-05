import logging
from pathlib import Path
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver

if __package__:
    from .brave_jina_search import BraveJinaSearchResults
else:
    from brave_jina_search import BraveJinaSearchResults

load_dotenv()

NOTES_FILE = Path("agent_notes.md")

# Configure the logger
logging.basicConfig(
    level=logging.DEBUG,  # Minimum level to capture
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log message format
    filename="weather.log",  # Optional: write logs to a file
    filemode="w",  # 'w' to overwrite file each run, 'a' to append
)

@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression. Use for any arithmetic
    especially with large numbers or multiple operations.
    Example: calculator("(15 * 23) + 100") returns "445"."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Error: {e}"

@tool
def fetch_url(url: str) -> str:
    """Fetch a web page and return readable text content.
    Use when you have a specific URL and need its full content.
    Returns up to 8000 characters."""
    try:
        response = httpx.get(url, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)[:8000]
    except Exception as e:
        return f"Error fetching URL: {e}"

@tool
def save_note(title: str, content: str) -> str:
    """Save a research note to disk for later reference.
    Args:
        title: a short descriptive title for the note
        content: the body of the note
    """
    NOTES_FILE.touch(exist_ok=True)
    with NOTES_FILE.open("a") as f:
        f.write(f"\n## {title}\n\n{content}\n")
    return f"Note '{title}' saved."

@tool
def read_notes() -> str:
    """Read the saved notes file. Use at the start of a session
    or when the user asks what has been covered."""
    if not NOTES_FILE.exists():
        return "No notes yet."
    return NOTES_FILE.read_text()

search_tool = BraveJinaSearchResults(max_results=5)
model = ChatOllama(model="qwen3.5:9b", temperature=0, keep_alive=-1, request_timeout=300)
checkpointer = MemorySaver()

agent = create_agent(
    model=model,
    tools=[calculator, search_tool, fetch_url, save_note, read_notes],
    system_prompt="""You are a research assistant with persistent notes. Use web
search and fetch_url to research, calculator for math, and save_note to
record key findings. Use read_notes to recall what has been covered.
Always cite specific sources from search results.""",
    checkpointer=checkpointer,
)

def run_interactive() -> None:
    config = {"configurable": {"thread_id": "research-session-1"}}
    print("Agent ready. Type 'quit' to exit.\n")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user_input.lower() in {"quit", "exit", "bye"}:
            break
        if not user_input:
            continue
        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
        )
        print(f"\nAgent: {result['messages'][-1].content}\n")

if __name__ == "__main__":
    run_interactive()
