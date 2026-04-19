import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from tiny_agent.builtin_tools import (
    execute_python,
    execute_shell,
    fetch_webpage,
    read_file,
    write_file,
)
from tiny_agent.agent import Agent


@pytest.mark.asyncio
async def test_execute_python():
    result = await execute_python.__tool__.execute(code="print('Hello')")
    assert "Hello" in result

    error_result = await execute_python.__tool__.execute(code="print(1/0)")
    assert "ZeroDivisionError" in error_result


@pytest.mark.asyncio
async def test_execute_shell():
    result = await execute_shell.__tool__.execute(command="echo 'Bash'")
    assert "Bash" in result

    error_result = await execute_shell.__tool__.execute(
        command="nonexistent_command_123"
    )
    assert "not found" in error_result


@pytest.mark.asyncio
@patch("urllib.request.urlopen")
async def test_fetch_webpage(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = b"<html><body><p>Test content</p></body></html>"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    result = await fetch_webpage.__tool__.execute(url="http://example.com")
    assert "Test content" in result

    mock_urlopen.side_effect = Exception("Mock network error")
    error_result = await fetch_webpage.__tool__.execute(url="http://invalid.com")
    assert "Failed to fetch URL: Mock network error" in error_result


@pytest.mark.asyncio
async def test_file_operations():
    with tempfile.TemporaryDirectory() as temp_dir:
        filepath = os.path.join(temp_dir, "test.txt")

        write_res = await write_file.__tool__.execute(
            filepath=filepath, content="File test"
        )
        assert "Successfully wrote" in write_res

        read_res = await read_file.__tool__.execute(filepath=filepath)
        assert read_res == "File test"

        error_res = await read_file.__tool__.execute(
            filepath=os.path.join(temp_dir, "fake.txt")
        )
        assert "Error reading file" in error_res


@pytest.mark.asyncio
async def test_agent_loads_builtin_tools():
    agent_with_builtins = Agent(session_id="test1")
    assert "execute_python" in agent_with_builtins.tools
    assert "execute_shell" in agent_with_builtins.tools

    agent_without_builtins = Agent(session_id="test2", load_builtin_tools=False)
    assert "execute_python" not in agent_without_builtins.tools
