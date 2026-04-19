import asyncio
from tiny_agent.agent import Agent
from tiny_agent.tools import tool
from tiny_agent.memory import SessionMemory


@tool()
def search_my_past_memories(query: str) -> str:
    results = SessionMemory.search_past_sessions(query=query, limit=5)
    return str(results) if results else "No past memories found."


async def main():
    agent = Agent(
        session_id="demo-session-456",
        model="gemini/gemini-2.5-flash",
        context_window_ratio=0.8,
        tools=[search_my_past_memories],
    )

    print("Agent starting...")
    print("Agent: ", end="")
    async for chunk in agent.run(
        "Hello! Can you search my past memories for anything related to 'tiny-agent'?"
    ):
        if chunk["type"] == "content":
            print(chunk["content"], end="", flush=True)
        elif chunk["type"] == "tool_start":
            print(f"\n[Tool calling: {chunk['name']}]")
        elif chunk["type"] == "tool_end":
            print(f"[Tool finished: {chunk['name']}]")
        elif chunk["type"] == "error":
            print(f"\n[Error: {chunk['content']}]")
    print()


if __name__ == "__main__":
    asyncio.run(main())
