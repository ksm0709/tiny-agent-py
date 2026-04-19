<!-- Generated: 2026-04-19 | Updated: 2026-04-19 -->

# tiny-agent-py

## Purpose
A hyper-minimalist, `litellm`-based AI agent framework for Python. Provides the essential primitives — streaming tool-calling loop, sliding-window SQLite memory, MCP client support, and markdown-based skill injection — without the overhead of larger frameworks like LangChain or AutoGen. Intended for embedding into CLI tools, bots, or lightweight scripts.

## Key Files

| File | Description |
|------|-------------|
| `pyproject.toml` | Project metadata, dependencies (`litellm`, `pydantic`, `mcp`, `pyyaml`), and build config (hatchling) |
| `example.py` | Runnable demo showing custom tool registration and cross-session memory search |
| `README.md` | User-facing quickstart guide and feature overview |
| `CHANGELOG.md` | Semantic-release-generated changelog |
| `uv.lock` | Locked dependency manifest for `uv` |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `tiny_agent/` | Core Python package — agent loop, tools, memory, MCP, skills (see `tiny_agent/AGENTS.md`) |
| `tests/` | pytest test suite covering all core modules (see `tests/AGENTS.md`) |
| `docs/` | Feature-level Markdown documentation (see `docs/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- **Language**: all code in English; conversation/docs in Korean per project policy
- **Package manager**: use `uv` for dependency management (`uv sync --dev` to install dev deps)
- **Entry point**: `tiny_agent/` is the only installable package; root-level `example.py` is a demo script only
- **Versioning**: managed by `python-semantic-release`; `version` lives in both `pyproject.toml` and `tiny_agent/__init__.py`

### Testing Requirements
```bash
uv run pytest --cov=tiny_agent        # run with coverage
uv run ruff check                     # lint
```
- Minimum 80% code coverage enforced in CI
- Tests must run in isolated temp directories (no writes to the project root)
- All async tests use `pytest-asyncio`

### Common Patterns
- Custom tools: decorate any Python function with `@tool()` from `tiny_agent.tools`
- Agent instantiation always requires a `session_id` string
- `agent.run(user_input)` is an async generator yielding `{"type": ..., ...}` dicts
- MCP tools are namespaced as `mcp__{server_name}__{tool_name}`

## Dependencies

### External
- `litellm >=1.0.0` — unified LLM routing (100+ providers)
- `pydantic >=2.0.0` — data validation
- `mcp >=1.0.0` — Model Context Protocol client
- `pyyaml >=6.0` — YAML front-matter parsing for skill files
- `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff` — dev/test tooling

<!-- MANUAL: -->
