import asyncio
import json
import litellm
from typing import List, Dict, Any, Callable, Optional, Union
from litellm import acompletion

from .memory import SessionMemory
from .skills import SkillLoader
from .mcp_manager import MCPManager
from .tools import Tool


class Agent:
    def __init__(
        self,
        session_id: str,
        model: str = "openai/gpt-5.4-mini",
        system_prompt: str = "You are a helpful assistant.",
        context_window_ratio: float = 0.8,
        max_iterations: float = float("inf"),
        tools: Optional[List[Callable]] = None,
        mcp_servers: Optional[List[Dict[str, Any]]] = None,
        instruction_dirs: Optional[List[str]] = None,
        skills_dirs: Optional[List[str]] = None,
        hooks: Optional[Dict[str, Union[Callable, List[Callable]]]] = None,
        load_builtin_tools: bool = True,
        litellm_kwargs: Optional[Dict[str, Any]] = None,
    ):
        self.session_id = session_id
        self.model = model
        self.max_iterations = max_iterations
        self.litellm_kwargs = litellm_kwargs or {}

        try:
            from litellm.utils import get_supported_openai_params

            supported_params = get_supported_openai_params(model=self.model) or []

            # Auto-enable reasoning if the model supports it and client didn't specify
            model_lower = self.model.lower()
            if "thinking" in supported_params and "thinking" not in self.litellm_kwargs:
                if "anthropic" in model_lower or "claude" in model_lower:
                    self.litellm_kwargs["thinking"] = {
                        "type": "enabled",
                        "budget_tokens": 4096,
                    }

            if (
                "reasoning_effort" in supported_params
                and "reasoning_effort" not in self.litellm_kwargs
            ):
                if not ("anthropic" in model_lower or "claude" in model_lower):
                    self.litellm_kwargs["reasoning_effort"] = "medium"

        except Exception:
            pass

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
                description="Loads detailed instructions for a skill by its ID. Use when you need to understand how to use a specific skill.",
            )
            self.tools["load_skill"] = load_skill_tool

        async def turn_start(goal: str) -> str:
            await self._call_hook("on_turn_start", goal, self)
            return f"Turn started with goal: {goal}"

        async def turn_stop(result: str) -> str:
            if getattr(self, "tasks", None):
                pending_tasks = [
                    t
                    for t in self.tasks
                    if str(t.get("status", "pending")).lower()
                    not in ["done", "completed", "[x]", "x", "cancelled"]
                ]
                if pending_tasks:
                    return f"Error: Cannot stop turn. There are {len(pending_tasks)} pending tasks remaining. Please complete or cancel them using the manage_tasks tool first."

            await self._call_hook("on_turn_stop", result, self)
            return f"Turn stopped with result: {result}"

        self.tools["turn_start"] = Tool(
            func=turn_start,
            name="turn_start",
            description="Call at the start of your turn to declare the task goal. Essential for tracking progress.",
        )
        self.tools["turn_stop"] = Tool(
            func=turn_stop,
            name="turn_stop",
            description="Call at the end of your turn to declare task completion and provide the final result. Ensures all pending tasks are finished.",
        )
        self.system_prompt += "\n\nYou MUST call the `turn_start` tool at the beginning of your work to declare your goal. When you have completed your task, you MUST call the `turn_stop` tool to provide the final result. If the work is complex and multi-step, you MUST use the `manage_tasks` tool to plan your work before executing it."

        self.tasks = []

        def manage_tasks(tasks: Union[List[Dict[str, str]], str]) -> str:
            if isinstance(tasks, str):
                try:
                    tasks = json.loads(tasks)
                except Exception:
                    return "Error: tasks must be a valid JSON array of objects."

            self.tasks = tasks
            print("\n" + "=" * 40)
            print("📝 TASK LIST UPDATED")
            print("=" * 40)
            for t in tasks:
                status = str(t.get("status", "pending")).lower()
                title = t.get("title", "Untitled")

                if status in ["done", "completed", "[x]", "x"]:
                    status_icon = "[x]"
                elif status in ["in_progress", "working", "[-]", "-"]:
                    status_icon = "[-]"
                else:
                    status_icon = "[ ]"

                print(f"{status_icon} {title}")
            print("=" * 40 + "\n")
            return "Task list updated successfully. The tasks are now pinned to your system prompt."

        self.tools["manage_tasks"] = Tool(
            func=manage_tasks,
            name="manage_tasks",
            description="Manage the agent's task list. Tasks are pinned to the context window. Provide a JSON array of objects with 'status' ('pending', 'in_progress', 'done'), 'title', and 'description'.",
        )

    async def _call_hook(self, hook_name: str, *args, **kwargs):
        if hook_name in self.hooks:
            hooks_val = self.hooks[hook_name]
            hooks_list = hooks_val if isinstance(hooks_val, list) else [hooks_val]

            results = []
            for hook in hooks_list:
                if asyncio.iscoroutinefunction(hook):
                    results.append(await hook(*args, **kwargs))
                else:
                    results.append(hook(*args, **kwargs))

            return results[0] if len(results) == 1 else results

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

            current_system_prompt = self.system_prompt
            if getattr(self, "tasks", None):
                current_system_prompt += "\n\n<current_tasks>\n"
                for i, t in enumerate(self.tasks):
                    current_system_prompt += f"Task {i + 1}:\n"
                    current_system_prompt += f"  Status: {t.get('status', 'pending')}\n"
                    current_system_prompt += f"  Title: {t.get('title', 'Untitled')}\n"
                    if "description" in t:
                        current_system_prompt += f"  Description: {t['description']}\n"
                current_system_prompt += "</current_tasks>\n"

            messages = [{"role": "system", "content": current_system_prompt}]
            messages.extend(self.memory.get_window())

            await self._call_hook("pre_call", messages, self)

            tools_schema = await self._get_all_tool_schemas()
            kwargs = {"model": self.model, "messages": messages, "stream": True}
            kwargs.update(self.litellm_kwargs)
            if tools_schema:
                kwargs["tools"] = tools_schema

            response = await acompletion(**kwargs)

            collected_content = ""
            collected_reasoning = ""
            tool_calls_dict = {}

            async for chunk in response:
                delta = chunk.choices[0].delta

                if getattr(delta, "reasoning_content", None):
                    collected_reasoning += delta.reasoning_content
                    yield {"type": "reasoning", "content": delta.reasoning_content}

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
            if collected_reasoning:
                message_dump["reasoning_content"] = collected_reasoning
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
