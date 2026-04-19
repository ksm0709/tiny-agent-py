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
        model="openai/gpt-4o-mini",
        context_window_ratio=0.8,
        tools=[search_my_past_memories],
    )

    print("Agent starting...")
    res = await agent.run(
        "Hello! Can you search my past memories for anything related to 'tiny-agent'?"
    )
    print("Agent:", res)


if __name__ == "__main__":
    asyncio.run(main())
