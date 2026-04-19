import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from tiny_agent.agent import Agent
from tiny_agent.tools import tool


@tool(name="local_calculator", description="Adds two integers")
def local_calculator(a: int, b: int) -> int:
    return a + b


@pytest.mark.asyncio
@patch("litellm.token_counter", return_value=100)
@patch("tiny_agent.agent.acompletion")
@patch("tiny_agent.mcp_manager.MCPManager.connect_all")
@patch("tiny_agent.mcp_manager.MCPManager.execute_tool")
@patch("tiny_agent.mcp_manager.MCPManager.close_all")
async def test_agent_end_to_end_flow(
    mock_close_all,
    mock_execute_tool,
    mock_connect_all,
    mock_acompletion,
    mock_token_counter,
):
    with tempfile.TemporaryDirectory() as temp_dir:
        skill_dir = os.path.join(temp_dir, "skills")
        os.makedirs(skill_dir)
        with open(os.path.join(skill_dir, "AGENTS.md"), "w") as f:
            f.write("Global E2E Project Instructions")

        with open(os.path.join(skill_dir, "e2e_skill.md"), "w") as f:
            f.write(
                "---\nname: e2e_skill\ndescription: test skill\n---\nSkill instructions."
            )

        hook_events = []

        def on_pre_call(messages, agent):
            hook_events.append("pre_call")

        async def on_tool_start(name, arguments, agent):
            hook_events.append(f"tool_start:{name}")

        agent = Agent(
            session_id="e2e_session",
            model="openai/gpt-4o-mini",
            context_window_ratio=0.8,
            tools=[local_calculator],
            mcp_servers=[{"name": "mock_db", "command": "dummy"}],
            skills_dirs=[skill_dir],
            instruction_dirs=[skill_dir],
            hooks={"pre_call": on_pre_call, "on_tool_start": on_tool_start},
        )

        agent.mcp_manager.mcp_tools["mcp__mock_db__query"] = {
            "session": MagicMock(),
            "original_name": "query",
            "schema": {
                "type": "function",
                "function": {
                    "name": "mcp__mock_db__query",
                    "description": "Query the database",
                    "parameters": {
                        "type": "object",
                        "properties": {"sql": {"type": "string"}},
                    },
                },
            },
        }

        mock_execute_tool.return_value = "Mocked DB Result"

        mock_tc1 = MagicMock()
        mock_tc1.index = 0
        mock_tc1.id = "call_local"
        mock_tc1.function.name = "local_calculator"
        mock_tc1.function.arguments = '{"a": 5, "b": 10}'

        mock_tc2 = MagicMock()
        mock_tc2.index = 1
        mock_tc2.id = "call_mcp"
        mock_tc2.function.name = "mcp__mock_db__query"
        mock_tc2.function.arguments = '{"sql": "SELECT 1"}'

        mock_chunk_turn1 = MagicMock()
        mock_chunk_turn1.choices = [MagicMock()]
        mock_chunk_turn1.choices[0].delta.content = None
        mock_chunk_turn1.choices[0].delta.tool_calls = [mock_tc1, mock_tc2]

        async def response_turn1():
            yield mock_chunk_turn1

        mock_chunk_turn2 = MagicMock()
        mock_chunk_turn2.choices = [MagicMock()]
        mock_chunk_turn2.choices[
            0
        ].delta.content = "Calculated 15 and queried the database successfully."
        mock_chunk_turn2.choices[0].delta.tool_calls = None

        async def response_turn2():
            yield mock_chunk_turn2

        mock_acompletion.side_effect = [response_turn1(), response_turn2()]

        responses = []
        async for chunk in agent.run("Calculate 5+10 and query the database"):
            responses.append(chunk)

        assert "pre_call" in hook_events
        assert "tool_start:local_calculator" in hook_events
        assert "tool_start:mcp__mock_db__query" in hook_events

        mock_execute_tool.assert_called_once_with(
            "mcp__mock_db__query", {"sql": "SELECT 1"}
        )

        tool_starts = [r["name"] for r in responses if r.get("type") == "tool_start"]
        assert "local_calculator" in tool_starts
        assert "mcp__mock_db__query" in tool_starts

        tool_ends = {
            r["name"]: r["result"] for r in responses if r.get("type") == "tool_end"
        }
        assert tool_ends["local_calculator"] == "15"
        assert tool_ends["mcp__mock_db__query"] == "Mocked DB Result"

        content_chunks = [r["content"] for r in responses if r.get("type") == "content"]
        assert "Calculated 15" in "".join(content_chunks)

        window = agent.memory.get_window()
        assert len(window) == 5
        assert (
            window[-1]["content"]
            == "Calculated 15 and queried the database successfully."
        )

        assert "Global E2E Project Instructions" in agent.system_prompt
        assert "e2e_skill" in agent.system_prompt
