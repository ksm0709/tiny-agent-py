<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-19 | Updated: 2026-04-19 -->

# tiny_agent

## Purpose
The sole installable Python package in this repository. Implements the complete agent framework: an async streaming LLM loop (`agent.py`), a type-safe tool registration system (`tools.py`), a sliding-window SQLite memory layer (`memory.py`), an MCP stdio client (`mcp_manager.py`), and a markdown-based skill loader (`skills.py`). Five built-in tools are auto-loaded at agent startup (`builtin_tools.py`).

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | Package version (`__version__ = "0.1.2"`) |
| `agent.py` | `Agent` class — core async generator loop, tool dispatch, hook system, MCP integration |
| `tools.py` | `Tool` class and `@tool` decorator — auto-generates JSON schema from Python type hints |
| `builtin_tools.py` | Five built-in tools loaded by default: `execute_python`, `execute_shell`, `fetch_webpage`, `read_file`, `write_file` |
| `memory.py` | `SessionMemory` — in-memory sliding window with SQLite spillover and FTS5 cross-session search |
| `mcp_manager.py` | `MCPManager` — connects to stdio MCP servers, discovers tools, proxies calls |
| `skills.py` | `Skill`, `SkillLoader` — loads `AGENTS.md` project context and YAML-front-matter skill files into the system prompt |

## For AI Agents

### Working In This Directory
- All modules are imported as `from tiny_agent.X import Y` — no relative imports at the top level
- `agent.py` uses `from .memory import SessionMemory` etc. (relative imports within package)
- Adding a new built-in tool: implement with `@tool()`, add to `BUILTIN_TOOLS` list in `builtin_tools.py`
- Adding a new module: register exports in `__init__.py` only if it is part of the public API

### Agent Lifecycle
```
Agent.__init__()
  └─ loads builtin tools + user tools
  └─ creates MCPManager (lazy connect)
  └─ loads skills (AGENTS.md + *.md files)

agent.run(user_input)  ← async generator
  └─ mcp_manager.connect_all()
  └─ loop (max_iterations):
       ├─ memory.get_window() → build messages
       ├─ acompletion(stream=True) → yield content chunks
       ├─ if tool_calls → _execute_tool() → yield tool_start/tool_end
       └─ if no tool_calls → mcp_manager.close_all(); return
  └─ on exhaustion → yield {"type": "error", "content": "Max iterations..."}
```

### Tool Namespacing
- Regular tools: registered by `tool.name` in `Agent.tools` dict
- MCP tools: namespaced `mcp__{server_name}__{tool_name}` — routed through `MCPManager`

### Memory Architecture
- In-memory `window` list is the active context
- When `litellm.token_counter()` exceeds `max_window_tokens`, oldest messages spill to SQLite
- SQLite DB stored at `~/.tiny-agent/sessions/{session_id}.db`
- FTS5 virtual table enables full-text cross-session search

### Testing Requirements
- Mock `acompletion` via `@patch("tiny_agent.agent.acompletion")` for agent loop tests
- Use `tempfile.TemporaryDirectory()` for any test that touches the filesystem
- Async tests require `@pytest.mark.asyncio`

### Common Patterns
```python
# Define a tool
@tool(name="my_tool", description="Does X")
def my_tool(param: str) -> str:
    return param.upper()

# Initialize agent
agent = Agent(
    session_id="unique-id",
    model="openai/gpt-5.4-mini",
    tools=[my_tool],
    hooks={"on_tool_start": my_hook},
)

# Stream responses
async for chunk in agent.run("query"):
    if chunk["type"] == "content":
        print(chunk["content"], end="")
```

## Dependencies

### Internal
- All modules are self-contained within this package
- `agent.py` imports from `memory`, `skills`, `mcp_manager`, `builtin_tools`

### External
- `litellm` — `acompletion`, `token_counter`, `get_model_info`
- `mcp` — `stdio_client`, `ClientSession`, `StdioServerParameters`
- `pyyaml` — YAML front-matter parsing in `skills.py`
- `sqlite3`, `subprocess`, `urllib.request` — stdlib only (no extra deps)

<!-- MANUAL: -->
