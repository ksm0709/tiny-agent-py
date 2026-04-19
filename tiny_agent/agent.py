import asyncio
import json
import litellm
import os
from typing import List, Dict, Any, Callable, Optional
from litellm import acompletion

from .memory import SessionMemory
from .skills import SkillLoader
from .mcp_manager import MCPManager
from .tools import Tool


class Agent:
    def __init__(
        self,
        session_id: str,
        model: str = "openai/gpt-4o-mini",
        system_prompt: str = "You are a helpful assistant.",
        context_window_ratio: float = 0.8,
        max_iterations: int = 10,
        tools: Optional[List[Callable]] = None,
        mcp_servers: Optional[List[Dict[str, Any]]] = None,
        instruction_dirs: Optional[List[str]] = None,
        skills_dirs: Optional[List[str]] = None,
        hooks: Optional[Dict[str, Callable]] = None,
        load_builtin_tools: bool = True,
    ):
        self.session_id = session_id
        self.model = model
        self.max_iterations = max_iterations

        model_info = {}
        try:
            model_info = litellm.get_model_info(model) or {}
        except Exception:
            pass
        max_tokens = model_info.get("max_input_tokens", 8000)
        self.max_window_tokens = int(max_tokens * context_window_ratio)

        self.memory = SessionMemory(
            session_id=session_id, model=model, max_window_tokens=self.max_window_tokens
        )

        self.tools = {}
        if load_builtin_tools:
            from .builtin_tools import BUILTIN_TOOLS

            for t in BUILTIN_TOOLS:
                self.tools[getattr(t, "__tool__").name] = getattr(t, "__tool__")

        for t in tools or []:
            if hasattr(t, "__tool__"):
                self.tools[getattr(t, "__tool__").name] = getattr(t, "__tool__")

        self.mcp_manager = MCPManager(mcp_servers or [])
        self.hooks = hooks or {}

        self.system_prompt = system_prompt
        self._load_instructions(instruction_dirs or [])
        self._load_skills(skills_dirs or [])

    def _load_instructions(self, dirs: List[str]):
        for d in dirs:
            agents_md = SkillLoader.load_agents_md(d)
            if agents_md:
                self.system_prompt += f"\n\n<project_instructions>\n--- Project Instructions (AGENTS.md) ---\n{agents_md}\n</project_instructions>"

    def _load_skills(self, dirs: List[str]):
        self.loaded_skills = SkillLoader.scan_skills(dirs)

        if self.loaded_skills:
            self.system_prompt += "\n\n<skill>\n--- Available Skills ---\n"
            for skill_id, s in self.loaded_skills.items():
                self.system_prompt += f"Skill ID: {skill_id}\nName: {s.name}\nDescription: {s.description}\n\n"
            self.system_prompt += "</skill>"
            self.system_prompt += "\nUse the `load_skill` tool with the appropriate `Skill ID` to load the full instructions for a skill."

        def load_skill(skill_id: str) -> str:
            if skill_id in self.loaded_skills:
                return self.loaded_skills[skill_id].instructions
            return f"Skill {skill_id} not found."

        if self.loaded_skills:
            load_skill_tool = Tool(
                func=load_skill,
                name="load_skill",
                description="Loads the detailed instructions for a specific skill by its ID.",
            )
            self.tools["load_skill"] = load_skill_tool

    async def _call_hook(self, hook_name: str, *args, **kwargs):
        if hook_name in self.hooks:
            hook = self.hooks[hook_name]
            if asyncio.iscoroutinefunction(hook):
                return await hook(*args, **kwargs)
            else:
                return hook(*args, **kwargs)

    async def _get_all_tool_schemas(self) -> List[Dict[str, Any]]:
        schemas = [t.get_schema() for t in self.tools.values()]
        schemas.extend(self.mcp_manager.get_all_tool_schemas())
        return schemas

    async def _execute_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        await self._call_hook("on_tool_start", name, arguments, self)
        result = ""
        if name in self.tools:
            result = await self.tools[name].execute(**arguments)
        elif name.startswith("mcp__"):
            result = await self.mcp_manager.execute_tool(name, arguments)
        else:
            result = f"Error: Tool {name} not found."
        await self._call_hook("on_tool_end", name, result, self)
        return result

    async def run(self, user_input: str):
        await self.mcp_manager.connect_all()
        self.memory.add_message({"role": "user", "content": user_input})

        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.memory.get_window())

            await self._call_hook("pre_call", messages, self)

            tools_schema = await self._get_all_tool_schemas()
            kwargs = {"model": self.model, "messages": messages, "stream": True}
            if tools_schema:
                kwargs["tools"] = tools_schema

            response = await acompletion(**kwargs)

            collected_content = ""
            tool_calls_dict = {}

            async for chunk in response:
                delta = chunk.choices[0].delta

                if delta.content:
                    collected_content += delta.content
                    yield {"type": "content", "content": delta.content}

                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        if tc.index not in tool_calls_dict:
                            tool_calls_dict[tc.index] = {
                                "id": tc.id,
                                "type": "function",
                                "function": {"name": tc.function.name, "arguments": ""},
                            }
                        if tc.function.arguments:
                            tool_calls_dict[tc.index]["function"]["arguments"] += (
                                tc.function.arguments
                            )

            tool_calls = list(tool_calls_dict.values()) if tool_calls_dict else None

            message_dump = {"role": "assistant"}
            if collected_content:
                message_dump["content"] = collected_content
            if tool_calls:
                message_dump["tool_calls"] = tool_calls

            await self._call_hook("post_call", message_dump, self)
            self.memory.add_message(message_dump)

            if tool_calls:
                for tool_call in tool_calls:
                    func_name = tool_call["function"]["name"]
                    yield {"type": "tool_start", "name": func_name}

                    try:
                        func_args = json.loads(tool_call["function"]["arguments"])
                        tool_result = await self._execute_tool(func_name, func_args)
                    except Exception as e:
                        tool_result = f"Error processing arguments: {str(e)}"

                    yield {"type": "tool_end", "name": func_name, "result": tool_result}

                    self.memory.add_message(
                        {
                            "role": "tool",
                            "name": func_name,
                            "tool_call_id": tool_call["id"],
                            "content": tool_result,
                        }
                    )
                continue

            await self.mcp_manager.close_all()
            return

        await self.mcp_manager.close_all()
        yield {
            "type": "error",
            "content": f"Max iterations ({self.max_iterations}) reached.",
        }
