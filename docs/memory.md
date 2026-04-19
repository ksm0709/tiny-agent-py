# Memory Management

`tiny-agent-py` uses a sliding-window memory approach backed by a per-session SQLite database. This ensures the LLM's context window stays within limits while persisting the full conversation history.

## Sliding-Window Context
The agent dynamically calculates the token size of the messages and ensures that the working memory stays below a certain percentage of the model's total token limit.
This is controlled by the `context_window_ratio` parameter (default 0.8, or 80%) during agent initialization.

## SQLite Spillover
When the token count of messages exceeds the calculated limit, the oldest messages are offloaded (spilled over) into a local SQLite database (`.tiny_agent_memory.db` by default). This guarantees that:
1. You never exceed LLM token limits.
2. The complete conversation history is preserved across agent restarts.

## Cross-Session Search
The agent has built-in capabilities to search past sessions, allowing it to retrieve information that was spilled over or discussed in entirely different sessions.
