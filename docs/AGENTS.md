<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-19 | Updated: 2026-04-19 -->

# docs

## Purpose
User-facing feature documentation written in Markdown. Each file corresponds to one major capability of `tiny_agent/`. These docs are referenced from `README.md` and are intended for end-users integrating the library, not for internal implementation notes.

## Key Files

| File | Description |
|------|-------------|
| `tools.md` | Guide to the `@tool` decorator — type hints, docstrings, schema generation, and registering tools with `Agent` |
| `builtin_tools.md` | Reference for the five auto-loaded built-in tools: Python REPL, Bash shell, web fetcher, file reader, file writer |
| `memory.md` | Explains the sliding-window context management and SQLite spillover architecture |
| `mcp.md` | How to configure and connect external MCP servers via the `mcp_servers` parameter |
| `skills.md` | How `AGENTS.md` project context and YAML-front-matter skill files are injected into the system prompt |

## For AI Agents

### Working In This Directory
- Keep docs tightly scoped to one feature per file — do not mix concerns
- Code examples must match the actual public API in `tiny_agent/`; verify against source before updating
- Do not document internal implementation details (SQLite schema, FTS5 triggers, etc.) — those belong in code comments
- When a public API changes, update the corresponding doc file in the same PR

### Common Patterns
- All code examples use `from tiny_agent.X import Y` import style
- Async examples use `asyncio.run(main())`

## Dependencies

### Internal
- `tools.md` → describes `tiny_agent/tools.py`
- `builtin_tools.md` → describes `tiny_agent/builtin_tools.py`
- `memory.md` → describes `tiny_agent/memory.py`
- `mcp.md` → describes `tiny_agent/mcp_manager.py`
- `skills.md` → describes `tiny_agent/skills.py`

<!-- MANUAL: -->
