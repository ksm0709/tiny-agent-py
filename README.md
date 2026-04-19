# tiny-agent-py

A hyper-minimalist, `litellm`-based agent framework with a sliding-window SQLite memory, native MCP support, and markdown-based skill loading.

Designed to be lightweight enough to import into CLI tools (like `pkm ask`) without the bloat of massive frameworks like LangChain.

## Features
- **LiteLLM Routing**: Supports 100+ LLMs easily.
- **Dynamic Context Window**: Keeps only the most recent N messages in the context window.
- **SQLite Spillover Memory**: Automatically archives older messages into a per-session SQLite database.
- **Cross-Session Search**: Built-in tools to search past sessions.
- **MCP Client Integration**: Connects seamlessly to external MCP servers via `stdio`.
- **Markdown Skills (`AGENTS.md`)**: Automatically loads project instructions and markdown-based skills into the system prompt.
- **@tool Decorator**: Easily expose any Python function as an agent tool.

## Installation
```bash
pip install -e .
```

## Basic Usage

```python
import asyncio
from tiny_agent.agent import Agent
from tiny_agent.tools import tool

@tool()
def get_current_weather(location: str) -> str:
    # A simple tool
    return f"The weather in {location} is sunny."

async def main():
    agent = Agent(
        session_id="session-123",
        model="openai/gpt-4o-mini",
        max_context_window=10,
        tools=[get_current_weather],
        mcp_servers=[
            {
                "name": "sqlite-mcp",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-sqlite", "--db", "test.db"]
            }
        ]
    )
    
    response = await agent.run("What is the weather in Seoul today?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## License
MIT License
