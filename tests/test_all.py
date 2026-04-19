import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from tiny_agent.agent import Agent
from tiny_agent.memory import SessionMemory
from tiny_agent.tools import tool


class TestTinyAgent(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_dir = os.path.join(self.temp_dir.name, "sessions")

    def tearDown(self):
        self.temp_dir.cleanup()

    async def test_session_memory_spill_over(self):
        memory = SessionMemory(
            session_id="test_session", max_window_messages=2, db_dir=self.db_dir
        )

        memory.add_message({"role": "user", "content": "msg1"})
        memory.add_message({"role": "assistant", "content": "msg2"})
        self.assertEqual(len(memory.get_window()), 2)

        memory.add_message({"role": "user", "content": "msg3"})
        self.assertEqual(len(memory.get_window()), 2)
        self.assertEqual(memory.get_window()[0]["content"], "msg2")
        self.assertEqual(memory.get_window()[1]["content"], "msg3")

        archived = memory.list_archived_messages()
        self.assertEqual(len(archived), 1)
        self.assertEqual(archived[0]["short_content"], "msg1")

    async def test_tools_decorator(self):
        @tool(name="add_numbers", description="Adds two numbers")
        def add(a: int, b: int) -> int:
            return a + b

        self.assertTrue(hasattr(add, "__tool__"))
        schema = add.__tool__.get_schema()
        self.assertEqual(schema["function"]["name"], "add_numbers")

        result = await add.__tool__.execute(a=5, b=3)
        self.assertEqual(result, "8")

    async def test_dynamic_skill_loading(self):
        skill_dir = os.path.join(self.temp_dir.name, "skills")
        os.makedirs(skill_dir)

        skill_file = os.path.join(skill_dir, "test_skill.md")
        with open(skill_file, "w") as f:
            f.write(
                "---\nname: test_skill\ndescription: A test skill\n---\nThis is a test skill."
            )

        agents_md = os.path.join(skill_dir, "AGENTS.md")
        with open(agents_md, "w") as f:
            f.write("Global agent instructions")

        agent = Agent(session_id="test_agent", skills_dirs=[skill_dir])

        self.assertIn("Global agent instructions", agent.system_prompt)
        self.assertIn("test_skill", agent.system_prompt)
        self.assertIn("A test skill", agent.system_prompt)

    @patch("tiny_agent.agent.acompletion")
    async def test_agent_run(self, mock_acompletion):
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

        self.assertTrue(
            any(
                r.get("type") == "content" and r.get("content") == "Hello from mock!"
                for r in responses
            )
        )
        self.assertEqual(len(agent.memory.get_window()), 2)


if __name__ == "__main__":
    unittest.main()
