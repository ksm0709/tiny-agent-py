# tiny-agent-py

A hyper-minimalist, `litellm`-based AI agent framework designed for speed, simplicity, and embeddability.

Unlike massive frameworks (e.g., LangChain, AutoGen), `tiny-agent-py` avoids bloat. It provides exactly what you need to build a capable agent: memory management, tool calling, MCP support, and dynamic skill loading. It is perfect for embedding into CLI tools, bots, or lightweight scripts.

## Core Features

- **LiteLLM Routing**: Access 100+ LLMs (OpenAI, Anthropic, Gemini, local models) with a unified API.
- **Dynamic Context Window**: Prevents context overflow by keeping the working memory under `N%` of the selected model's total context token limit.
- **SQLite Spillover Memory**: Archives older messages to a per-session SQLite database, ensuring full history retention without token limits.
- **Cross-Session Search**: Built-in tools for the agent to query past conversations.
- **Native Built-in Tools**: Essential tools (Python REPL, Bash Shell, Web Scraper, File I/O) are included and automatically loaded out-of-the-box.
- **Markdown Skills (`AGENTS.md`)**: Automatically injects project instructions and dynamic markdown-based skills into the system prompt.
- **`@tool` Decorator**: Turn any Python function into an LLM-accessible tool with zero boilerplate.

## Documentation

For deep dives into specific features, check out our documentation:
- [Built-in Tools](docs/builtin_tools.md) - Learn about the native REPL, Web Fetcher, and File Manager.
- [Memory Management](docs/memory.md) - Learn how the sliding-window and SQLite spillover work.
- [MCP Integration](docs/mcp.md) - How to connect to external MCP servers.
- [Tools & `@tool`](docs/tools.md) - Guide to writing custom Python tools.
- [Markdown Skills](docs/skills.md) - Managing `AGENTS.md` and dynamic skills.

## Installation

You can install `tiny-agent-py` directly via `pip` or `uv`:

```bash
pip install tiny-agent-py
# or
uv pip install tiny-agent-py
```

*For local development:*
```bash
git clone https://github.com/your-org/tiny-agent-py.git
cd tiny-agent-py
pip install -e .
```

## Basic Usage

Here is a quick example of how to spin up an agent with a custom tool and an external MCP server.

```python
import asyncio
from tiny_agent.agent import Agent
from tiny_agent.tools import tool

# 1. Define a custom Python tool
@tool()
def get_current_weather(location: str) -> str:
    """Returns the current weather for a given location."""
    return f"The weather in {location} is sunny and 22°C."

async def main():
    # 2. Initialize the agent
    agent = Agent(
        session_id="weather-session-001",
        model="openai/gpt-4o-mini",       # Powered by litellm
        context_window_ratio=0.8,         # Keeps context within 80% of model's max tokens
        tools=[get_current_weather],      # Inject custom tools
        mcp_servers=[                     # Connect to external MCP servers
            {
                "name": "sqlite-mcp",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-sqlite", "--db", "test.db"]
            }
        ]
    )
    
    # 3. Run the agent
    response = await agent.run("What is the weather in Seoul today? Also, check if test.db has any tables.")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## Testing & CI

We use `pytest` and enforce a minimum of 80% code coverage. Tests are automatically run via GitHub Actions on every push and pull request.

```bash
# Install dev dependencies
uv sync --dev

# Run tests with coverage
uv run pytest --cov=tiny_agent
```

## License

MIT License
