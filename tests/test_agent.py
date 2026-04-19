import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from tiny_agent.agent import Agent
from tiny_agent.tools import tool


@pytest.mark.asyncio
async def test_agent_load_skills_exception():
    with tempfile.TemporaryDirectory() as temp_dir:
        skill_file = os.path.join(temp_dir, "invalid_skill.md")
        with open(skill_file, "w") as f:
            f.write("invalid")

        with patch(
            "tiny_agent.skills.SkillLoader.load_from_file",
            side_effect=Exception("Load error"),
        ):
            agent = Agent(session_id="test", skills_dirs=[temp_dir])
            assert "invalid_skill" not in agent.system_prompt


@pytest.mark.asyncio
async def test_agent_call_hook():
    sync_hook_called = False

    def sync_hook(*args, **kwargs):
        nonlocal sync_hook_called
        sync_hook_called = True
        return "sync_result"

    async_hook_called = False

    async def async_hook(*args, **kwargs):
        nonlocal async_hook_called
        async_hook_called = True
        return "async_result"

    agent = Agent(session_id="test", hooks={"sync": sync_hook, "async": async_hook})

    res1 = await agent._call_hook("sync")
    assert sync_hook_called
    assert res1 == "sync_result"

    res2 = await agent._call_hook("async")
    assert async_hook_called
    assert res2 == "async_result"

    res3 = await agent._call_hook("nonexistent")
    assert res3 is None


@pytest.mark.asyncio
async def test_agent_call_multiple_hooks():
    calls = []

    def hook1(*args, **kwargs):
        calls.append("hook1")
        return 1

    async def hook2(*args, **kwargs):
        calls.append("hook2")
        return 2

    agent = Agent(session_id="test", hooks={"multi": [hook1, hook2]})

    res = await agent._call_hook("multi")
    assert calls == ["hook1", "hook2"]
    assert res == [1, 2]


@pytest.mark.asyncio
async def test_agent_execute_tool():
    @tool(name="test_tool")
    def my_tool(x: int):
        return x * 2

    agent = Agent(session_id="test", tools=[my_tool])

    res1 = await agent._execute_tool("test_tool", {"x": 5})
    assert res1 == "10"

    agent.mcp_manager.execute_tool = AsyncMock(return_value="mcp_result")
    res2 = await agent._execute_tool("mcp__test__tool", {"arg": "val"})
    assert res2 == "mcp_result"
    agent.mcp_manager.execute_tool.assert_called_once_with(
        "mcp__test__tool", {"arg": "val"}
    )

    res3 = await agent._execute_tool("nonexistent", {})
    assert "not found" in res3


@pytest.mark.asyncio
@patch("tiny_agent.agent.acompletion")
async def test_agent_run_tool_calls(mock_acompletion):
    @tool(name="test_tool")
    def my_tool(x: int):
        return x * 2

    agent = Agent(session_id="test", tools=[my_tool], max_iterations=2)

    mock_tc = MagicMock()
    mock_tc.index = 0
    mock_tc.id = "call_123"
    mock_tc.function.name = "test_tool"
    mock_tc.function.arguments = '{"x": 5}'

    mock_chunk1 = MagicMock()
    mock_chunk1.choices = [MagicMock()]
    mock_chunk1.choices[0].delta.content = None
    mock_chunk1.choices[0].delta.tool_calls = [mock_tc]

    mock_chunk2 = MagicMock()
    mock_chunk2.choices = [MagicMock()]
    mock_chunk2.choices[0].delta.content = "Done"
    mock_chunk2.choices[0].delta.tool_calls = None

    async def mock_response1():
        yield mock_chunk1

    async def mock_response2():
        yield mock_chunk2

    mock_acompletion.side_effect = [mock_response1(), mock_response2()]

    responses = []
    async for chunk in agent.run("Hi"):
        responses.append(chunk)

    assert any(
        r.get("type") == "tool_start" and r.get("name") == "test_tool"
        for r in responses
    )
    assert any(
        r.get("type") == "tool_end"
        and r.get("name") == "test_tool"
        and r.get("result") == "10"
        for r in responses
    )
    assert any(
        r.get("type") == "content" and r.get("content") == "Done" for r in responses
    )


@pytest.mark.asyncio
@patch("tiny_agent.agent.acompletion")
async def test_agent_run_tool_call_exception(mock_acompletion):
    @tool(name="test_tool")
    def my_tool(x: int):
        return x * 2

    agent = Agent(session_id="test", tools=[my_tool], max_iterations=2)

    mock_tc = MagicMock()
    mock_tc.index = 0
    mock_tc.id = "call_123"
    mock_tc.function.name = "test_tool"
    mock_tc.function.arguments = "invalid json"

    mock_chunk1 = MagicMock()
    mock_chunk1.choices = [MagicMock()]
    mock_chunk1.choices[0].delta.content = None
    mock_chunk1.choices[0].delta.tool_calls = [mock_tc]

    mock_chunk2 = MagicMock()
    mock_chunk2.choices = [MagicMock()]
    mock_chunk2.choices[0].delta.content = "Done"
    mock_chunk2.choices[0].delta.tool_calls = None

    async def mock_response1():
        yield mock_chunk1

    async def mock_response2():
        yield mock_chunk2

    mock_acompletion.side_effect = [mock_response1(), mock_response2()]

    responses = []
    async for chunk in agent.run("Hi"):
        responses.append(chunk)

    assert any(
        r.get("type") == "tool_end"
        and "Error processing arguments" in r.get("result", "")
        for r in responses
    )


@pytest.mark.asyncio
@patch("tiny_agent.agent.acompletion")
async def test_agent_run_max_iterations(mock_acompletion):
    agent = Agent(session_id="test", max_iterations=1)

    mock_tc = MagicMock()
    mock_tc.index = 0
    mock_tc.id = "call_123"
    mock_tc.function.name = "nonexistent"
    mock_tc.function.arguments = "{}"

    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = None
    mock_chunk.choices[0].delta.tool_calls = [mock_tc]

    async def mock_response():
        yield mock_chunk

    mock_acompletion.return_value = mock_response()

    responses = []
    async for chunk in agent.run("Hi"):
        responses.append(chunk)

    assert any(
        r.get("type") == "error" and "Max iterations" in r.get("content", "")
        for r in responses
    )


@pytest.mark.asyncio
@patch("tiny_agent.agent.acompletion")
async def test_agent_run(mock_acompletion):
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Hello from mock!"
    mock_chunk.choices[0].delta.tool_calls = None

    async def mock_response():
        yield mock_chunk

    mock_acompletion.return_value = mock_response()

    agent = Agent(session_id="test_run", max_iterations=1)

    responses = []
    async for chunk in agent.run("Hi"):
        responses.append(chunk)

    assert any(
        r.get("type") == "content" and r.get("content") == "Hello from mock!"
        for r in responses
    )
    assert len(agent.memory.get_window()) == 2


@pytest.mark.asyncio
async def test_agent_turn_start_stop():
    start_called = False
    stop_called = False
    start_goal = None
    stop_result = None

    async def on_turn_start(goal, agent):
        nonlocal start_called, start_goal
        start_called = True
        start_goal = goal

    async def on_turn_stop(result, agent):
        nonlocal stop_called, stop_result
        stop_called = True
        stop_result = result

    agent = Agent(
        session_id="test_turns",
        hooks={"on_turn_start": on_turn_start, "on_turn_stop": on_turn_stop},
    )

    start_res = await agent._execute_tool("turn_start", {"goal": "my goal"})
    assert start_called
    assert start_goal == "my goal"
    assert "Turn started" in start_res

    stop_res = await agent._execute_tool("turn_stop", {"result": "my result"})
    assert stop_called
    assert stop_result == "my result"
    assert "Turn stopped" in stop_res
