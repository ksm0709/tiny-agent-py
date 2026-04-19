import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from tiny_agent.mcp_manager import MCPManager


@pytest.fixture
def mcp_servers():
    return [
        {
            "name": "test_server",
            "command": "node",
            "args": ["test.js"],
            "env": {"TEST": "1"},
        },
        {"name": "no_command_server"},
    ]


@pytest.mark.asyncio
@patch("tiny_agent.mcp_manager.stdio_client")
@patch("tiny_agent.mcp_manager.ClientSession")
async def test_connect_all(mock_client_session, mock_stdio_client, mcp_servers):
    mock_transport = (AsyncMock(), AsyncMock())

    mock_stdio_context = AsyncMock()
    mock_stdio_context.__aenter__.return_value = mock_transport
    mock_stdio_client.return_value = mock_stdio_context

    mock_session = AsyncMock()
    mock_session_context = AsyncMock()
    mock_session_context.__aenter__.return_value = mock_session
    mock_client_session.return_value = mock_session_context

    mock_tool = MagicMock()
    mock_tool.name = "test_tool"
    mock_tool.description = "A test tool"
    mock_tool.inputSchema = {"type": "object"}

    mock_tools_response = MagicMock()
    mock_tools_response.tools = [mock_tool]
    mock_session.list_tools.return_value = mock_tools_response

    manager = MCPManager(mcp_servers)
    await manager.connect_all()

    assert "test_server" in manager.sessions
    assert "mcp__test_server__test_tool" in manager.mcp_tools

    schemas = manager.get_all_tool_schemas()
    assert len(schemas) == 1
    assert schemas[0]["function"]["name"] == "mcp__test_server__test_tool"

    await manager.close_all()
    assert len(manager.sessions) == 0
    assert len(manager.mcp_tools) == 0


@pytest.mark.asyncio
@patch("tiny_agent.mcp_manager.stdio_client")
@patch("tiny_agent.mcp_manager.ClientSession")
async def test_connect_all_exception(
    mock_client_session, mock_stdio_client, mcp_servers
):
    mock_stdio_client.side_effect = Exception("Connection failed")

    manager = MCPManager(mcp_servers)
    await manager.connect_all()

    assert len(manager.sessions) == 0


@pytest.mark.asyncio
async def test_execute_tool_not_found():
    manager = MCPManager([])
    result = await manager.execute_tool("nonexistent_tool", {})
    assert "not found" in result


@pytest.mark.asyncio
async def test_execute_tool_success():
    manager = MCPManager([])
    mock_session = AsyncMock()

    mock_content = MagicMock()
    mock_content.type = "text"
    mock_content.text = "Tool output"

    mock_result = MagicMock()
    mock_result.isError = False
    mock_result.content = [mock_content]

    mock_session.call_tool.return_value = mock_result

    manager.mcp_tools["test_tool"] = {
        "session": mock_session,
        "original_name": "orig_tool",
    }

    result = await manager.execute_tool("test_tool", {"arg": "val"})
    assert result == "Tool output"
    mock_session.call_tool.assert_called_once_with(
        "orig_tool", arguments={"arg": "val"}
    )


@pytest.mark.asyncio
async def test_execute_tool_error():
    manager = MCPManager([])
    mock_session = AsyncMock()

    mock_result = MagicMock()
    mock_result.isError = True
    mock_result.content = "Error message"

    mock_session.call_tool.return_value = mock_result

    manager.mcp_tools["test_tool"] = {
        "session": mock_session,
        "original_name": "orig_tool",
    }

    result = await manager.execute_tool("test_tool", {})
    assert "MCP Tool Error: Error message" in result


@pytest.mark.asyncio
async def test_execute_tool_exception():
    manager = MCPManager([])
    mock_session = AsyncMock()
    mock_session.call_tool.side_effect = Exception("Execution failed")

    manager.mcp_tools["test_tool"] = {
        "session": mock_session,
        "original_name": "orig_tool",
    }

    result = await manager.execute_tool("test_tool", {})
    assert "MCP Tool Execution Exception: Execution failed" in result
