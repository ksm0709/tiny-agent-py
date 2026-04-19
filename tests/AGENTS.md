<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-19 | Updated: 2026-04-19 -->

# tests

## Purpose
pytest test suite providing unit and integration coverage for all modules in `tiny_agent/`. Tests are structured one-to-one with source modules. Async tests use `pytest-asyncio`; external LLM calls are always mocked via `unittest.mock`.

## Key Files

| File | Description |
|------|-------------|
| `test_agent.py` | Agent loop tests: hook dispatch, tool execution, streaming, max-iteration cutoff, argument parse errors |
| `test_tools.py` | `Tool` class and `@tool` decorator: schema generation, sync/async execution, JSON serialization, error handling |
| `test_builtin_tools.py` | Built-in tool tests: `execute_python`, `execute_shell`, `fetch_webpage`, `read_file`, `write_file` |
| `test_memory.py` | `SessionMemory` tests: window management, SQLite spillover, FTS5 search, session cleanup |
| `test_mcp_manager.py` | `MCPManager` tests: connection, tool schema retrieval, tool execution, error paths |
| `test_skills.py` | `SkillLoader` tests: YAML front-matter parsing, `AGENTS.md` loading, missing-file handling |
| `test_e2e.py` | End-to-end integration tests combining agent, tools, and memory |

## For AI Agents

### Working In This Directory
- **Never** write to the project root or `~/.tiny-agent/` directly — use `tempfile.TemporaryDirectory()` for any filesystem operations
- Mock `acompletion` at `tiny_agent.agent.acompletion` (not at the `litellm` module level) to control LLM responses
- MCP connections are mocked via `AsyncMock` on `MCPManager` methods — do not spin up real MCP servers in tests
- All test functions touching `agent.run()` must be `async def` with `@pytest.mark.asyncio`

### Testing Requirements
```bash
uv run pytest                          # run all tests
uv run pytest tests/test_agent.py -v   # run a single file
uv run pytest --cov=tiny_agent         # with coverage report
```
- 80% coverage minimum enforced by CI (`.github/workflows/test.yml`)
- Each new module added to `tiny_agent/` needs a corresponding `test_*.py` file

### Common Patterns
```python
# Mocking acompletion for streaming
@pytest.mark.asyncio
@patch("tiny_agent.agent.acompletion")
async def test_something(mock_acompletion):
    async def mock_response():
        yield mock_chunk
    mock_acompletion.return_value = mock_response()
    ...

# Filesystem isolation
with tempfile.TemporaryDirectory() as tmp:
    agent = Agent(session_id="test", ...)
```

## Dependencies

### Internal
- All imports are from `tiny_agent.*`

### External
- `pytest`, `pytest-asyncio` — test runner and async support
- `pytest-cov` — coverage reporting
- `unittest.mock` — `patch`, `MagicMock`, `AsyncMock` (stdlib)

<!-- MANUAL: -->
