import asyncio
from typing import Dict, Any, List
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
from mcp import StdioServerParameters

class MCPManager:
    def __init__(self, mcp_servers: List[Dict[str, Any]]):
        self.mcp_servers = mcp_servers
        self.sessions: Dict[str, ClientSession] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        self._exit_stack = []

    async def connect_all(self):
        for server in self.mcp_servers:
            server_name = server.get("name", "unknown")
            command = server.get("command")
            args = server.get("args", [])
            env = server.get("env", None)
            
            if not command:
                continue

            try:
                params = StdioServerParameters(command=command, args=args, env=env)
                from contextlib import AsyncExitStack
                stack = AsyncExitStack()
                self._exit_stack.append(stack)

                transport = await stack.enter_async_context(stdio_client(params))
                read, write = transport
                session = await stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                
                self.sessions[server_name] = session
                tools_response = await session.list_tools()
                
                for t in tools_response.tools:
                    tool_id = f"mcp__{server_name}__{t.name}"
                    self.mcp_tools[tool_id] = {
                        "session": session,
                        "original_name": t.name,
                        "schema": {
                            "type": "function",
                            "function": {
                                "name": tool_id,
                                "description": t.description or "",
                                "parameters": t.inputSchema
                            }
                        }
                    }
            except Exception as e:
                print(f"[Warning] Failed to connect to MCP server '{server_name}': {e}")
                continue

    def get_all_tool_schemas(self) -> List[Dict[str, Any]]:
        return [tool_data["schema"] for tool_data in self.mcp_tools.values()]

    async def execute_tool(self, tool_id: str, arguments: Dict[str, Any]) -> str:
        if tool_id not in self.mcp_tools:
            return f"Error: MCP tool {tool_id} not found."
        
        tool_data = self.mcp_tools[tool_id]
        session = tool_data["session"]
        original_name = tool_data["original_name"]
        
        try:
            result = await session.call_tool(original_name, arguments=arguments)
            if result.isError:
                return f"MCP Tool Error: {result.content}"
            return "\n".join([c.text for c in result.content if c.type == "text"])
        except Exception as e:
            return f"MCP Tool Execution Exception: {str(e)}"

    async def close_all(self):
        for stack in reversed(self._exit_stack):
            await stack.aclose()
        self._exit_stack.clear()
        self.sessions.clear()
        self.mcp_tools.clear()
