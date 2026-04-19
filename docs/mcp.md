# MCP (Model Context Protocol) Integration

`tiny-agent-py` natively supports external MCP servers, allowing you to instantly extend the agent's capabilities with tools provided by the community.

## Configuration
When initializing the `Agent`, you can pass a list of MCP server configurations. The agent connects to these servers via `stdio`.

```python
agent = Agent(
    mcp_servers=[
        {
            "name": "sqlite-mcp",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sqlite", "--db", "test.db"]
        }
    ]
)
```

## How It Works
1. Upon initialization, the agent connects to the specified MCP servers.
2. It fetches all available tools from each MCP server.
3. These tools are automatically registered and made available to the LLM.
4. When the LLM decides to call an MCP tool, the agent routes the call to the corresponding MCP server and returns the result to the LLM.
